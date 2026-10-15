"""LaTeX fixtures shared by the template tests.

The body fixtures deliberately reuse each template's own `BODY` skeleton. That
matters: `BODY` only contains macros the template actually defines, so appending
copies of it is guaranteed to compile, while still being long enough to force a
multi-page document.
"""

# Identity injected per call. Distinct from any template's module-level INFO so
# a leak back to import-time constants is immediately visible in the output.
INJECTED_INFO = {
    "fullname": "Priya Raghunathan",
    "email": "priya.raghunathan@example.org",
    "phone": "+1 415-555-0139",
    "location": "Seattle, WA",
    "links": [
        ("github.com/priyaraghu", "https://github.com/priyaraghu"),
        ("linkedin.com/in/priya-raghunathan", "https://linkedin.com/in/priya-raghunathan"),
    ],
}

# The name every template shipped with before `assemble()` gained an `info`
# argument. Must never reach a rendered PDF.
LEGACY_BAKED_IN_NAME = "Jordan Avery"


def short_model_output(module) -> str:
    """A realistic model response: the template's own format, body untouched.

    `module.format` is LOCKED_TOP + BODY_MARK + BODY -- exactly what the LLM is
    asked to echo back, including the header it must not edit.
    """
    return module.format


def long_model_output(module, repeats: int = 3) -> str:
    """The same skeleton with the body repeated, to force several pages.

    This is what exposed the sidebar bug: a `tabular` cannot break across pages,
    so an over-long body pushed the entire unbreakable box to page 2 and left
    page 1 blank.
    """
    _, marker, body = module.format.partition(module.BODY_MARK)
    assert marker, f"{module.__name__} has no BODY_MARK"
    return "PREAMBLE" + marker + ("\n" + body) * repeats