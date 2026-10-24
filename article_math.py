import re

# Wikipedia exports each formula twice: a plain-text fallback split one symbol
# per line, then the LaTeX source as {\displaystyle ...}. These helpers drop the
# fallback and wrap the LaTeX in $...$ so st.markdown renders it with KaTeX.

MATH_START = re.compile(r"\{\\(?:display|text)style\b")
FUNCTION_NAMES = re.compile(r"\\(sin|cos|tan|cot|sec|csc|arcsin|arccos|arctan|sinh|cosh|tanh|"
                            r"log|ln|exp|lim|max|min|sup|inf|det|gcd|deg|dim|ker|arg|mod|Pr)\b")
INVISIBLE = "⁠⁡⁢⁣"  # word joiner and invisible math operators
LIST_MARKER = re.compile(r"^\s*(?:[:*+-]|\d+\.)\s+")
SYMBOLS = {
    "\\Delta": "Δ", "\\delta": "δ", "\\alpha": "α", "\\beta": "β", "\\gamma": "γ",
    "\\theta": "θ", "\\lambda": "λ", "\\mu": "μ", "\\pi": "π", "\\sigma": "σ",
    "\\Sigma": "Σ", "\\omega": "ω", "\\Omega": "Ω", "\\phi": "φ", "\\varphi": "φ",
    "\\epsilon": "ε", "\\varepsilon": "ε", "\\rho": "ρ", "\\tau": "τ", "\\nu": "ν",
    "\\times": "×", "\\cdot": "⋅", "\\div": "÷", "\\pm": "±", "\\leq": "≤",
    "\\geq": "≥", "\\neq": "≠", "\\approx": "≈", "\\infty": "∞", "\\to": "→",
    "\\sum": "∑", "\\int": "∫", "\\sqrt": "√", "\\in": "∈", "\\ldots": "…",
    "\\cdots": "⋯", "\\circ": "∘", "\\star": "⋆", "\\partial": "∂", "\\nabla": "∇",
}


def find_math(text, start=0):
    # Return (begin, end, latex) for the next {\displaystyle ...}, matching braces
    match = MATH_START.search(text, start)
    if match is None:
        return None
    begin = match.start()
    depth = 0
    i = begin
    while i < len(text):
        char = text[i]
        if char == "\\":
            i += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                latex = text[match.end():i].strip()
                return begin, i + 1, latex.replace("\\_", "_").replace("\\*", "*")
        i += 1
    return None


def visible_chars(latex):
    # Roughly what the formula looks like as plain text, for matching the fallback
    text = latex
    for command, symbol in sorted(SYMBOLS.items(), key=lambda item: -len(item[0])):
        text = text.replace(command, symbol)
    text = FUNCTION_NAMES.sub(r"\1", text)  # \cos shows as "cos"
    text = re.sub(r"\\[A-Za-z]+|\\.", "", text)
    return re.sub(r"[{}_^&\s]", "", text).replace("\u2212", "-")


def is_fallback(piece, visible):
    piece = re.sub(rf"[\s{INVISIBLE}]", "", piece).replace("\u2212", "-")
    if piece == "" or piece in visible or (len(piece) <= 2 and not piece.isascii()):
        return True
    # Brackets drawn around matrices don't appear in the LaTeX source
    return set(piece) <= set("[](){}|⟨⟩‖,.")


def join_text(before, math, after):
    before = before.rstrip(" \u2060\xa0")
    after = after.lstrip(" \u2060\xa0")
    left = " " if before and not before.endswith(("(", " ")) else ""
    right = "" if not after or after[0] in ".,;:)!?" else " "
    return f"{before}{left}{math}{right}{after}"


def convert_inline(line):
    # Formulas that share a line with other text, e.g. table cells
    result = ""
    position = 0
    while (found := find_math(line, position)) is not None:
        begin, end, latex = found
        before = line[position:begin]
        visible = visible_chars(latex)
        words = before.rstrip().split(" ")
        while words and words[-1] != "" and is_fallback(words[-1], visible):
            words.pop()
            while words and words[-1] == "":
                words.pop()
        result += join_text(" ".join(words), f"${latex}$", "")
        position = end
    return result + line[position:]


def format_math(body):
    # Escape existing dollar signs so prices don't turn into math
    lines = body.replace("$", "\\$").split("\n")
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        found = find_math(stripped)
        whole_line = found is not None and found[0] == 0 and found[1] == len(stripped)

        if not whole_line:
            output.append(convert_inline(line) if MATH_START.search(line) else line)
            i += 1
            continue

        latex = found[2]
        visible = visible_chars(latex)

        # Drop the one-symbol-per-line fallback above the LaTeX
        while output and is_fallback(output[-1], visible):
            if output[-1].strip() == "" and len(output) > 1 and not is_fallback(output[-2], visible):
                break
            output.pop()
        while output and output[-1].strip() == "":
            output.pop()

        # The fallback can start on a list or definition line, e.g. "* E" or ":   P"
        before = output.pop() if output else ""
        marker = LIST_MARKER.match(before)
        if marker:
            tail = before[marker.end():]
            if is_fallback(tail, visible):
                before = before[:marker.end()]

        after = lines[i + 1] if i + 1 < len(lines) else ""
        joins_sentence = after.strip() != "" and not after.lstrip().startswith(("#", "|", "* ", "- "))
        ends_sentence = not joins_sentence or after.strip() in {".", ","}

        # Matrices and multi-line equations are too tall to sit inside a sentence
        multiline = "\\begin{" in latex
        definition = before.strip() == ":"
        after_colon = before.rstrip().endswith(":") and not marker
        display = multiline or definition or (after_colon and ends_sentence)

        if display:
            if before.strip() and not definition:
                output.append(before)
            output.extend(["", "$$", latex, "$$", ""])
            if joins_sentence:
                if after.strip() not in {".", ","}:
                    output.append(after.lstrip(" ⁠\xa0"))
                i += 1
        else:
            if joins_sentence:
                output.append(join_text(before, f"${latex}$", after))
                i += 1
            else:
                output.append(join_text(before, f"${latex}$", ""))
        i += 1

    # Streamlit doesn't support ":   term" definition lists, so show them as bullets
    return re.sub(r"^:\s+", "- ", "\n".join(output), flags=re.M)
