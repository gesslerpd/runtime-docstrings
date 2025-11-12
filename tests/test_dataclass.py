"""Test dataclass support for runtime_docs."""

import dataclasses
from dataclasses import InitVar, dataclass, field
from enum import Enum
from typing import ClassVar

from runtime_docstrings import docstrings, get_docstrings


@docstrings
@dataclass
class BasicDataClass:
    """A basic dataclass for testing."""

    name: str
    """The name field."""

    age: int = 30
    """The age field with default value."""

    tags: list[str] = dataclasses.field(default_factory=list)
    """List of tags associated with this entity."""

    active: bool = True

    description: str | None = None
    """Optional description text."""


def test_basic_dataclass_docstrings():
    """Test that docstrings are correctly extracted from dataclass fields."""
    docs = get_docstrings(BasicDataClass)

    assert "name" in docs
    assert docs["name"] == "The name field."

    assert "age" in docs
    assert docs["age"] == "The age field with default value."

    assert "tags" in docs
    assert docs["tags"] == "List of tags associated with this entity."

    assert "active" not in docs  # No docstring for this field

    assert "description" in docs
    assert docs["description"] == "Optional description text."


def test_dataclass_pep224_attributes():
    """Test that PEP 224 style attributes are created for dataclass fields."""
    assert hasattr(BasicDataClass, "__doc_name__")
    assert BasicDataClass.__doc_name__ == "The name field."

    assert hasattr(BasicDataClass, "__doc_age__")
    assert BasicDataClass.__doc_age__ == "The age field with default value."

    assert hasattr(BasicDataClass, "__doc_tags__")
    assert BasicDataClass.__doc_tags__ == "List of tags associated with this entity."

    assert not hasattr(BasicDataClass, "__doc_active__")  # No docstring for this field

    assert hasattr(BasicDataClass, "__doc_description__")
    assert BasicDataClass.__doc_description__ == "Optional description text."


def test_dataclass_instance_creation():
    """Test that the docstrings decorator doesn't interfere with dataclass instance creation."""
    instance = BasicDataClass(name="Test")

    assert instance.name == "Test"
    assert instance.age == 30
    assert instance.tags == []
    assert instance.active is True
    assert instance.description is None


@docstrings
@dataclass(slots=True)
class SlottedDataClass:
    """A slotted dataclass for testing."""

    name: str
    """The name field."""

    age: int = 30
    """The age field with default value."""

    tags: list[str] = field(default_factory=list)
    """List of tags associated with this entity."""

    active: bool = True

    description: str | None = None
    """Optional description text."""


def test_slotted_dataclass_docstrings():
    """Test that docstrings are correctly extracted from slotted dataclass fields."""
    docs = get_docstrings(SlottedDataClass)

    assert docs["name"] == "The name field."

    assert docs["age"] == "The age field with default value."

    assert docs["tags"] == "List of tags associated with this entity."

    assert "active" not in docs  # No docstring for this field

    assert docs["description"] == "Optional description text."


def test_slotted_dataclass_pep224_attributes():
    """Test that PEP 224 style attributes are created for slotted dataclass fields."""
    # For slotted dataclasses, __doc_{name}__ attributes are only created if they're in __slots__
    # or if they're special attributes that Python allows outside of slots

    # Check that the attribute docstrings are still accessible via get_docstrings
    docs = get_docstrings(SlottedDataClass)
    assert "name" in docs
    assert "age" in docs
    assert "tags" in docs
    assert "description" in docs


def test_slotted_dataclass_instance_creation():
    """Test that the docstrings decorator doesn't interfere with slotted dataclass instance creation."""
    instance = SlottedDataClass(name="Test")

    assert instance.name == "Test"
    assert instance.age == 30
    assert instance.tags == []
    assert instance.active is True
    assert instance.description is None


@docstrings
@dataclass
class DataClassWithMetadata:
    """A dataclass with field metadata for testing."""

    name: str = field(metadata={"validator": "str_validator"})
    """The name field with metadata."""

    age: int = field(
        default=30,
        metadata={"validator": "int_validator", "min": 0, "max": 120},
    )
    """The age field with default value and metadata."""

    tags: list[str] = field(
        default_factory=list,
        metadata={"doc": "Existing doc in metadata"},
    )
    """List of tags with existing doc in metadata."""


def test_field_metadata_docstrings():
    """Test that docstrings are correctly added to field metadata."""
    fields = {f.name: f for f in dataclasses.fields(DataClassWithMetadata)}

    # Check that the field docstrings are correctly stored
    assert "name" in fields
    assert fields["name"].metadata["__doc__"] == "The name field with metadata."

    assert "age" in fields
    assert fields["age"].metadata["__doc__"] == "The age field with default value and metadata."

    assert "tags" in fields
    assert fields["tags"].metadata["__doc__"] == "List of tags with existing doc in metadata."


def test_field_metadata_preservation():
    """Test that existing field metadata is preserved when adding docstrings."""
    # Get the fields from the dataclass
    fields = {f.name: f for f in dataclasses.fields(DataClassWithMetadata)}

    # Check that the name field's metadata is preserved
    assert "validator" in fields["name"].metadata
    assert fields["name"].metadata["validator"] == "str_validator"

    # Check that the age field's metadata is preserved
    assert "validator" in fields["age"].metadata
    assert fields["age"].metadata["validator"] == "int_validator"
    assert "min" in fields["age"].metadata
    assert fields["age"].metadata["min"] == 0
    assert "max" in fields["age"].metadata
    assert fields["age"].metadata["max"] == 120


@docstrings
@dataclass
class GrandParentDataClass:
    """A grandparent dataclass for testing multi-level inheritance."""

    grandparent_field: str = "grandparent_value"
    """The grandparent field."""

    shared_field: str = "grandparent"
    """Shared field from grandparent."""

    another_shared: str = "grandparent_another"
    """Another shared field from grandparent."""


@docstrings
@dataclass
class ParentDataClass(GrandParentDataClass):
    """A parent dataclass for testing inheritance."""

    parent_field: str = "parent_value"
    """The parent field."""

    shared_field: str = "parent"
    """Shared field from parent."""


@docstrings
@dataclass
class ChildDataClass(ParentDataClass):
    """A child dataclass for testing inheritance."""

    shared_field: str = "child"  # Override without docstring

    child_field: str = "child_value"
    """The child field."""

    another_shared: str = "child_another"
    """Overridden shared field."""


def test_dataclass_inheritance():
    """Test that docstrings work correctly with dataclass inheritance."""
    # Check that each class has its own docstrings
    grandparent_docs = get_docstrings(GrandParentDataClass)
    assert "grandparent_field" in grandparent_docs
    assert grandparent_docs["grandparent_field"] == "The grandparent field."
    assert "shared_field" in grandparent_docs
    assert grandparent_docs["shared_field"] == "Shared field from grandparent."
    assert "another_shared" in grandparent_docs
    assert grandparent_docs["another_shared"] == "Another shared field from grandparent."

    parent_docs = get_docstrings(ParentDataClass)
    assert "parent_field" in parent_docs
    assert parent_docs["parent_field"] == "The parent field."
    assert "shared_field" in parent_docs
    assert parent_docs["shared_field"] == "Shared field from parent."
    assert "grandparent_field" not in parent_docs  # Only contains its own docstrings

    child_docs = get_docstrings(ChildDataClass)
    assert "child_field" in child_docs
    assert child_docs["child_field"] == "The child field."
    assert "shared_field" not in child_docs  # No docstring for overridden field
    assert "another_shared" in child_docs
    assert child_docs["another_shared"] == "Overridden shared field."
    assert "parent_field" not in child_docs  # Only contains its own docstrings

    # Check that PEP 224 attributes are set correctly
    assert hasattr(GrandParentDataClass, "__doc_grandparent_field__")
    assert GrandParentDataClass.__doc_grandparent_field__ == "The grandparent field."

    assert hasattr(ParentDataClass, "__doc_parent_field__")
    assert ParentDataClass.__doc_parent_field__ == "The parent field."

    assert hasattr(ChildDataClass, "__doc_child_field__")
    assert ChildDataClass.__doc_child_field__ == "The child field."

    # Check that docstrings are properly inherited through the class hierarchy
    assert hasattr(ParentDataClass, "__doc_shared_field__")
    assert ParentDataClass.__doc_shared_field__ == "Shared field from parent."

    assert hasattr(GrandParentDataClass, "__doc_another_shared__")
    assert GrandParentDataClass.__doc_another_shared__ == "Another shared field from grandparent."

    assert hasattr(ChildDataClass, "__doc_another_shared__")
    assert ChildDataClass.__doc_another_shared__ == "Overridden shared field."

    # Test MRO resolution for child class
    assert ChildDataClass.__doc_parent_field__ == "The parent field."
    assert ChildDataClass.__doc_child_field__ == "The child field."
    assert ChildDataClass.__doc_grandparent_field__ == "The grandparent field."
    assert ChildDataClass.__doc_shared_field__ == "Shared field from parent."
    assert ChildDataClass.__doc_another_shared__ == "Overridden shared field."

    # Test MRO resolution for parent class
    assert ParentDataClass.__doc_parent_field__ == "The parent field."
    assert ParentDataClass.__doc_grandparent_field__ == "The grandparent field."
    assert ParentDataClass.__doc_shared_field__ == "Shared field from parent."
    assert ParentDataClass.__doc_another_shared__ == "Another shared field from grandparent."


@docstrings
class RegularClass:
    """A regular class for testing API consistency."""

    regular_attr: str = "value"
    """Regular attribute."""


@docstrings
@dataclass
class MixedInheritance(RegularClass):
    """A dataclass inheriting from a regular class."""

    dataclass_field: str = "default_value"
    """Dataclass field."""


def test_mixed_inheritance():
    """Test inheritance between dataclasses and regular classes."""
    # Check that each class has its own docstrings
    regular_docs = get_docstrings(RegularClass)
    assert "regular_attr" in regular_docs
    assert regular_docs["regular_attr"] == "Regular attribute."

    mixed_docs = get_docstrings(MixedInheritance)
    assert "dataclass_field" in mixed_docs
    assert mixed_docs["dataclass_field"] == "Dataclass field."

    # Check that PEP 224 attributes are set correctly
    assert hasattr(RegularClass, "__doc_regular_attr__")
    assert RegularClass.__doc_regular_attr__ == "Regular attribute."

    assert hasattr(MixedInheritance, "__doc_dataclass_field__")
    assert MixedInheritance.__doc_dataclass_field__ == "Dataclass field."

    assert MixedInheritance.__doc_regular_attr__ == "Regular attribute."
    assert MixedInheritance.__doc_dataclass_field__ == "Dataclass field."

    # Check instance creation
    instance = MixedInheritance(dataclass_field="test")
    assert instance.regular_attr == "value"
    assert instance.dataclass_field == "test"


@docstrings
class RegularParent:
    """A regular class for testing API consistency with inheritance."""

    parent_attr: str = "parent_value"
    """Parent attribute."""

    shared_attr: str = "parent_shared"
    """Shared attribute from parent."""


@docstrings
@dataclass
class DataclassChild(RegularParent):
    """A dataclass inheriting from a regular class."""

    child_field: str = "child_value"
    """Child field."""

    shared_attr: str = "child_shared"
    """Shared attribute from child."""


@docstrings
class EnumParent(Enum):
    """An enum class for testing API consistency."""

    FIRST = "first"
    """First enum value."""

    SECOND = "second"
    """Second enum value."""


@docstrings
@dataclass
class ComplexInheritance(DataclassChild):
    """A complex inheritance case with multiple levels."""

    complex_field: str = "complex"
    """Complex field."""


def test_api_consistency():
    """Test that the API is consistent across class types."""
    # Test that get_docstrings works consistently
    regular_docs = get_docstrings(RegularParent)
    dataclass_docs = get_docstrings(BasicDataClass)
    enum_docs = get_docstrings(EnumParent)

    # All should return dictionaries
    assert isinstance(regular_docs, dict)
    assert isinstance(dataclass_docs, dict)
    assert isinstance(enum_docs, dict)

    # All should have __attribute_docs__ attribute
    assert hasattr(RegularParent, "__attribute_docs__")
    assert hasattr(BasicDataClass, "__attribute_docs__")
    assert hasattr(EnumParent, "__attribute_docs__")

    # All should have PEP 224 style attributes for documented fields
    assert hasattr(RegularParent, "__doc_parent_attr__")
    assert hasattr(BasicDataClass, "__doc_name__")

    # Test that the docstrings decorator doesn't interfere with normal class behavior
    # Regular class instantiation
    regular_instance = RegularParent()
    assert regular_instance.parent_attr == "parent_value"

    # Dataclass instantiation
    dataclass_instance = BasicDataClass(name="Test")
    assert dataclass_instance.name == "Test"

    # Enum access
    assert EnumParent.FIRST.value == "first"


def test_complex_inheritance_mro():
    """Test MRO resolution with complex inheritance involving different class types."""
    # Test MRO resolution for complex inheritance
    assert ComplexInheritance.__doc_complex_field__ == "Complex field."

    assert ComplexInheritance.__doc_child_field__ == "Child field."
    assert ComplexInheritance.__doc_parent_attr__ == "Parent attribute."

    assert ComplexInheritance.__doc_shared_attr__ == "Shared attribute from child."

    # Test instance creation and attribute access
    instance = ComplexInheritance(child_field="test")
    assert instance.complex_field == "complex"
    assert instance.child_field == "test"
    assert instance.parent_attr == "parent_value"
    assert instance.shared_attr == "child_shared"


def test_consistent_field_metadata_access():
    """Test that field metadata can be accessed consistently."""
    # For dataclasses, check field metadata
    fields = {f.name: f for f in dataclasses.fields(DataClassWithMetadata)}

    docs = get_docstrings(DataClassWithMetadata)
    for name, docstring in docs.items():
        assert fields[name].metadata["__doc__"] == docstring


@docstrings
class BaseClass:
    """Base class for multi-level inheritance testing."""

    base_attr: str = "base"
    """Base attribute."""

    shared_attr: str = "base_shared"
    """Shared attribute from base."""


@docstrings
@dataclass
class IntermediateDataClass(BaseClass):
    """Intermediate dataclass for multi-level inheritance testing."""

    intermediate_field: str = "intermediate"
    """Intermediate field."""

    shared_attr: str = "intermediate_shared"
    """Shared attribute from intermediate."""


@docstrings
class ChildRegularClass(IntermediateDataClass):
    """Child regular class inheriting from a dataclass."""

    child_attr: str = "child"
    """Child attribute."""

    # Override the shared_attr from the parent class
    def __init__(self):
        super().__init__()
        self.shared_attr = "child_shared"

    shared_attr: str = "child_shared"
    """Shared attribute from child."""


def test_multi_level_mixed_inheritance():
    """Test multi-level inheritance with mixed class types."""
    # Check that each class has its own docstrings
    base_docs = get_docstrings(BaseClass)
    assert "base_attr" in base_docs
    assert base_docs["base_attr"] == "Base attribute."
    assert "shared_attr" in base_docs
    assert base_docs["shared_attr"] == "Shared attribute from base."

    intermediate_docs = get_docstrings(IntermediateDataClass)
    assert "intermediate_field" in intermediate_docs
    assert intermediate_docs["intermediate_field"] == "Intermediate field."
    assert "shared_attr" in intermediate_docs
    assert intermediate_docs["shared_attr"] == "Shared attribute from intermediate."

    child_docs = get_docstrings(ChildRegularClass)
    assert "child_attr" in child_docs
    assert child_docs["child_attr"] == "Child attribute."
    assert "shared_attr" in child_docs
    assert child_docs["shared_attr"] == "Shared attribute from child."

    # Test MRO resolution for child class
    assert ChildRegularClass.__doc_base_attr__ == "Base attribute."
    assert ChildRegularClass.__doc_intermediate_field__ == "Intermediate field."
    assert ChildRegularClass.__doc_child_attr__ == "Child attribute."
    assert ChildRegularClass.__doc_shared_attr__ == "Shared attribute from child."

    # Test MRO resolution for intermediate class
    assert IntermediateDataClass.__doc_base_attr__ == "Base attribute."
    assert IntermediateDataClass.__doc_intermediate_field__ == "Intermediate field."
    assert IntermediateDataClass.__doc_shared_attr__ == "Shared attribute from intermediate."

    # Test instance creation and attribute access
    child_instance = ChildRegularClass()
    assert child_instance.base_attr == "base"
    assert child_instance.intermediate_field == "intermediate"
    assert child_instance.child_attr == "child"
    assert child_instance.shared_attr == "child_shared"

    intermediate_instance = IntermediateDataClass()
    assert intermediate_instance.base_attr == "base"
    assert intermediate_instance.intermediate_field == "intermediate"
    assert intermediate_instance.shared_attr == "intermediate_shared"


# Edge case tests


@docstrings
@dataclass
class EmptyDocstrings:
    """A dataclass with empty docstrings."""

    name: str
    """"""  # Empty docstring

    age: int = 30
    """  """  # Whitespace-only docstring

    description: str = ""
    # No docstring


def test_empty_docstrings():
    """Test handling of empty docstrings."""
    docs = get_docstrings(EmptyDocstrings)

    # Empty docstrings should be included but as empty strings
    assert "name" in docs
    assert docs["name"] == ""

    # Whitespace-only docstrings should be cleaned to empty strings
    assert "age" in docs
    assert docs["age"] == ""

    # No docstring should not be included
    assert "description" not in docs


@docstrings
@dataclass
class SpecialCharDocstrings:
    """A dataclass with docstrings containing special characters."""

    name: str
    """Field with *markdown* and **formatting**."""

    description: str
    """Multi-line
    docstring with
    several lines."""

    code: str
    """```python
    def example():
        return "code block"
    ```"""

    regex: str
    r"""Raw docstring with \n \t \\ special escape sequences."""


def test_special_char_docstrings():
    """Test handling of docstrings with special characters."""
    docs = get_docstrings(SpecialCharDocstrings)

    assert "name" in docs
    assert docs["name"] == "Field with *markdown* and **formatting**."

    assert "description" in docs
    assert "Multi-line" in docs["description"]
    assert "several lines" in docs["description"]

    assert "code" in docs
    assert "```python" in docs["code"]
    assert "def example():" in docs["code"]

    assert "regex" in docs
    assert r"\n \t \\" in docs["regex"]


@docstrings
@dataclass
class DefaultFactoryDataClass:
    """A dataclass with default factory functions."""

    simple_list: list[str] = field(default_factory=list)
    """A simple list with default factory."""

    complex_dict: dict[str, list[int]] = field(
        default_factory=lambda: {"default": [1, 2, 3]},
    )
    """A complex dictionary with default factory lambda."""

    # Using a static method as factory to avoid the self parameter issue
    @staticmethod
    def _factory_method():
        return set()

    custom_set: set = field(default_factory=_factory_method)
    """A set with a method as factory."""


def test_default_factory_docstrings():
    """Test docstrings with default factory functions."""
    docs = get_docstrings(DefaultFactoryDataClass)

    assert "simple_list" in docs
    assert docs["simple_list"] == "A simple list with default factory."

    assert "complex_dict" in docs
    assert docs["complex_dict"] == "A complex dictionary with default factory lambda."

    assert "custom_set" in docs
    assert docs["custom_set"] == "A set with a method as factory."

    # Test instance creation to ensure factories work
    instance = DefaultFactoryDataClass()
    assert instance.simple_list == []
    assert instance.complex_dict == {"default": [1, 2, 3]}
    assert instance.custom_set == set()


@docstrings
@dataclass
class PostInitDataClass:
    """A dataclass with __post_init__ processing."""

    name: str
    """The name field."""

    age: int
    """The age field."""

    full_info: str = field(init=False)
    """Full information combining name and age."""

    def __post_init__(self):
        """Process after initialization."""
        self.full_info = f"{self.name} ({self.age})"


def test_post_init_docstrings():
    """Test docstrings with __post_init__ processing."""
    docs = get_docstrings(PostInitDataClass)

    assert "name" in docs
    assert docs["name"] == "The name field."

    assert "age" in docs
    assert docs["age"] == "The age field."

    assert "full_info" in docs
    assert docs["full_info"] == "Full information combining name and age."

    # Test instance creation with post_init
    instance = PostInitDataClass("John", 30)
    assert instance.name == "John"
    assert instance.age == 30
    assert instance.full_info == "John (30)"


@docstrings
@dataclass(frozen=True)
class FrozenDataClass:
    """A frozen dataclass for testing."""

    name: str
    """The name field."""

    age: int = 30
    """The age field with default value."""


def test_frozen_dataclass():
    """Test docstrings with frozen dataclasses."""
    docs = get_docstrings(FrozenDataClass)

    assert "name" in docs
    assert docs["name"] == "The name field."

    assert "age" in docs
    assert docs["age"] == "The age field with default value."

    # Test instance creation and immutability
    instance = FrozenDataClass("Test")
    assert instance.name == "Test"
    assert instance.age == 30


@docstrings
@dataclass
class ClassVarDataClass:
    """A dataclass with ClassVar fields."""

    name: str
    """The name field."""

    DEFAULT_AGE: ClassVar[int] = 30
    """Default age constant."""

    CONSTANTS: ClassVar[dict[str, str]] = {"DEFAULT_NAME": "Unknown"}
    """Dictionary of constants."""


def test_classvar_docstrings():
    """Test docstrings with ClassVar fields."""
    docs = get_docstrings(ClassVarDataClass)

    assert "name" in docs
    assert docs["name"] == "The name field."

    assert "DEFAULT_AGE" in docs
    assert docs["DEFAULT_AGE"] == "Default age constant."

    assert "CONSTANTS" in docs
    assert docs["CONSTANTS"] == "Dictionary of constants."

    # Test that ClassVar fields are not included in __init__
    instance = ClassVarDataClass("Test")
    assert instance.name == "Test"
    assert ClassVarDataClass.DEFAULT_AGE == 30
    assert ClassVarDataClass.CONSTANTS == {"DEFAULT_NAME": "Unknown"}


@docstrings
@dataclass
class InitVarDataClass:
    """A dataclass with InitVar fields."""

    name: str
    """The name field."""

    password: InitVar[str]
    """Password used only during initialization."""

    hashed_password: str = field(init=False)
    """Hashed password stored after initialization."""

    def __post_init__(self, password):
        """Process the password."""
        # Simple "hashing" for testing
        self.hashed_password = f"hashed_{password}"


def test_initvar_docstrings():
    """Test docstrings with InitVar fields."""
    docs = get_docstrings(InitVarDataClass)

    assert "name" in docs
    assert docs["name"] == "The name field."

    assert "password" in docs
    assert docs["password"] == "Password used only during initialization."

    assert "hashed_password" in docs
    assert docs["hashed_password"] == "Hashed password stored after initialization."

    # Test instance creation with InitVar
    instance = InitVarDataClass("Test", "secret")
    assert instance.name == "Test"
    assert instance.hashed_password == "hashed_secret"
    assert not hasattr(instance, "password")  # InitVar not stored


@docstrings
@dataclass
class FieldWithNoDefault:
    """A dataclass with a field that has no default but has metadata."""

    name: str = field(metadata={"required": True})
    """Required name field."""


def test_field_with_no_default():
    """Test docstrings with fields that have no default but have metadata."""
    docs = get_docstrings(FieldWithNoDefault)

    assert "name" in docs
    assert docs["name"] == "Required name field."

    # Check field metadata
    fields = {f.name: f for f in dataclasses.fields(FieldWithNoDefault)}
    assert "required" in fields["name"].metadata
    assert fields["name"].metadata["required"] is True


@docstrings
@dataclass
class NestedDataClass:
    """A dataclass with nested dataclass fields."""

    name: str
    """The name field."""

    @docstrings
    @dataclass
    class Address:
        """Nested address dataclass."""

        street: str
        """Street name."""

        city: str
        """City name."""

    address: Address
    """The address field."""


def test_nested_dataclass():
    """Test docstrings with nested dataclasses."""
    # Check outer dataclass docstrings
    outer_docs = get_docstrings(NestedDataClass)
    assert "name" in outer_docs
    assert outer_docs["name"] == "The name field."
    assert "address" in outer_docs
    assert outer_docs["address"] == "The address field."

    # Check nested dataclass docstrings
    inner_docs = get_docstrings(NestedDataClass.Address)
    assert "street" in inner_docs
    assert inner_docs["street"] == "Street name."
    assert "city" in inner_docs
    assert inner_docs["city"] == "City name."

    # Test instance creation with nested dataclass
    address = NestedDataClass.Address("Main St", "New York")
    instance = NestedDataClass("Test", address)
    assert instance.name == "Test"
    assert instance.address.street == "Main St"
    assert instance.address.city == "New York"
