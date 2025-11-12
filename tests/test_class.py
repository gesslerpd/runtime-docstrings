from runtime_docstrings import docstrings, get_docstrings


def _prop(self):
    """Property.

    Returns: The property value.

    """
    return self.__doc__  # pragma: no cover


@docstrings
class Base:
    """Base class."""

    BASE_VAR = "base"
    """Represents a base variable."""

    ins_prop = property(_prop)
    """Instance property."""

    another_prop = property(_prop, doc="Another property.")
    """Another instance property."""

    """Ok"""
    OK: str = "ok"

    AL: str
    """Alright"""

    OKR = ""
    """okr"""

    @docstrings
    class Inner:
        """Inner class for demonstration."""

        INNER_VAR: int = 42
        """An inner variable."""
        INNER_VAR2: str = "inner"
        """Another inner variable."""


@docstrings
class Child(Base):
    BASE_VAR = "overridden_base"

    CHILD_VAR = "child"
    """Represents a child variable."""


@docstrings
class NoDocClass:
    """This class has no attribute docstrings."""

    """Test"""
    NO_DOC_VAR = "no_doc"

    HEY = 3


def test_no_doc_class():
    assert get_docstrings(NoDocClass) == {}


def test_all():
    assert get_docstrings(Base) == {
        "AL": "Alright",
        "OKR": "okr",
        "BASE_VAR": "Represents a base variable.",
        "another_prop": "Another instance property.",
        "ins_prop": "Instance property.",
    }
    assert get_docstrings(Base.Inner) == {
        "INNER_VAR": "An inner variable.",
        "INNER_VAR2": "Another inner variable.",
    }

    assert get_docstrings(Child) == {"CHILD_VAR": "Represents a child variable."}

    assert Child.__doc_BASE_VAR__ == "Represents a base variable."
    assert Child.__doc_CHILD_VAR__ == "Represents a child variable."
    assert Child.ins_prop.__doc__.startswith("Property.")
    assert Child.another_prop.__doc__ == "Another property."

    assert Child.__doc__ is None
    assert Base.__doc__ == "Base class."
