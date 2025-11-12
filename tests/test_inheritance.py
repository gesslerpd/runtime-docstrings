"""Test inheritance behaviors for runtime_docs."""

from runtime_docstrings import docstrings, get_docstrings


@docstrings
class GrandParent:
    """Grand parent class."""

    GRAND_VAR = "grand"
    """Grand parent variable."""

    SHARED_VAR = "grand_shared"
    """Shared variable from grand parent."""


@docstrings
class Parent(GrandParent):
    """Parent class."""

    PARENT_VAR = "parent"
    """Parent variable."""

    SHARED_VAR = "parent_shared"  # Override without docstring

    ANOTHER_SHARED = "parent_another"
    """Another shared variable."""


@docstrings
class Child(Parent):
    """Child class."""

    CHILD_VAR = "child"
    """Child variable."""

    ANOTHER_SHARED = "child_another"
    """Overridden shared variable."""


class NonDecoratedParent:
    """Non-decorated parent."""

    NON_DEC_VAR = "non_decorated"
    """This won't be parsed."""


@docstrings
class MixedChild(NonDecoratedParent):
    """Child of non-decorated parent."""

    MIXED_VAR = "mixed"
    """Mixed inheritance variable."""


def test_basic_inheritance():
    """Test that each class only returns its own docstrings."""
    grand_docs = get_docstrings(GrandParent)
    assert grand_docs == {
        "GRAND_VAR": "Grand parent variable.",
        "SHARED_VAR": "Shared variable from grand parent.",
    }

    parent_docs = get_docstrings(Parent)
    assert parent_docs == {
        "PARENT_VAR": "Parent variable.",
        "ANOTHER_SHARED": "Another shared variable.",
    }

    child_docs = get_docstrings(Child)
    assert child_docs == {
        "CHILD_VAR": "Child variable.",
        "ANOTHER_SHARED": "Overridden shared variable.",
    }


def test_mro_resolution():
    """Test MRO resolution for docstring access."""
    # Child can resolve its own docstrings
    assert Child.__doc_CHILD_VAR__ == "Child variable."

    # Child can resolve parent docstrings
    assert Child.__doc_PARENT_VAR__ == "Parent variable."

    # Child can resolve grandparent docstrings
    assert Child.__doc_GRAND_VAR__ == "Grand parent variable."

    # Child gets overridden version
    assert Child.__doc_ANOTHER_SHARED__ == "Overridden shared variable."

    # Child gets grandparent version for SHARED_VAR (parent has no docstring)
    assert Child.__doc_SHARED_VAR__ == "Shared variable from grand parent."


def test_pep224_attributes():
    """Test PEP 224 style __doc_name__ attributes."""
    assert Child.__doc_CHILD_VAR__ == "Child variable."

    assert Parent.__doc_PARENT_VAR__ == "Parent variable."

    assert GrandParent.__doc_GRAND_VAR__ == "Grand parent variable."


def test_inheritance_with_non_decorated_parent():
    """Test inheritance from non-decorated parent."""
    mixed_docs = get_docstrings(MixedChild)
    assert mixed_docs == {"MIXED_VAR": "Mixed inheritance variable."}

    # Non-decorated parent should not have __attribute_docs__
    assert not hasattr(NonDecoratedParent, "__attribute_docs__")
    assert not hasattr(MixedChild, "__doc_NON_DEC_VAR__")

    # Mixed child should have its own docs
    assert hasattr(MixedChild, "__attribute_docs__")


def test_attribute_access_inheritance():
    """Test that child instances can access parent attributes."""
    child = Child()

    # Child can access its own attributes
    assert child.CHILD_VAR == "child"

    # Child can access parent attributes
    assert child.PARENT_VAR == "parent"

    # Child can access grandparent attributes
    assert child.GRAND_VAR == "grand"

    # Child gets overridden values
    assert child.ANOTHER_SHARED == "child_another"
    assert child.SHARED_VAR == "parent_shared"  # Parent override


def test_class_docstring_inheritance():
    """Test that class docstrings work normally with inheritance."""
    assert GrandParent.__doc__ == "Grand parent class."
    assert Parent.__doc__ == "Parent class."
    assert Child.__doc__ == "Child class."

    # Child instance should have child's docstring
    child = Child()
    assert child.__class__.__doc__ == "Child class."


def test_multiple_inheritance():
    """Test multiple inheritance scenarios."""

    @docstrings
    class Mixin:
        """Mixin class."""

        MIXIN_VAR = "mixin"
        """Mixin variable."""

        CONFLICT_VAR = "mixin_conflict"
        """Mixin conflict variable."""

    @docstrings
    class Base:
        """Base class."""

        BASE_VAR = "base"
        """Base variable."""

        CONFLICT_VAR = "base_conflict"
        """Base conflict variable."""

    @docstrings
    class MultiChild(Mixin, Base):
        """Multiple inheritance child."""

        MULTI_VAR = "multi"
        """Multi child variable."""

    # Each class should have its own docs
    mixin_docs = get_docstrings(Mixin)
    assert "MIXIN_VAR" in mixin_docs

    base_docs = get_docstrings(Base)
    assert "BASE_VAR" in base_docs

    multi_docs = get_docstrings(MultiChild)
    assert multi_docs == {"MULTI_VAR": "Multi child variable."}

    assert MultiChild.__doc_CONFLICT_VAR__ == "Mixin conflict variable."
    assert MultiChild.__doc_MIXIN_VAR__ == "Mixin variable."
    assert MultiChild.__doc_BASE_VAR__ == "Base variable."
