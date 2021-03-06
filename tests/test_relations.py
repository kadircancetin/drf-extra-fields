from rest_framework import serializers
from rest_framework.test import APISimpleTestCase

from drf_extra_fields.relations import (
    PresentablePrimaryKeyRelatedField,
    PresentableSlugRelatedField,
)
from .utils import MockObject, MockQueryset


class PresentationSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {"pk": instance.pk, "name": instance.name}


class SerializerWithPresentable(serializers.Serializer):
    test_many_field = PresentablePrimaryKeyRelatedField(
        queryset=MockQueryset([]),
        presentation_serializer=PresentationSerializer,
        read_source="foo_property", many=True
    )
    test_function_field = PresentablePrimaryKeyRelatedField(
        queryset=MockQueryset([]),
        presentation_serializer=PresentationSerializer,
        read_source="foo_function", many=True
    )
    test_field = PresentablePrimaryKeyRelatedField(
        queryset=MockQueryset([MockObject(pk=1, name="foo")]),
        presentation_serializer=PresentationSerializer,
        read_source="bar_property", many=False
    )


class TestPresentablePrimaryKeyRelatedField(APISimpleTestCase):
    def setUp(self):
        self.queryset = MockQueryset(
            [
                MockObject(pk=1, name="foo"),
                MockObject(pk=2, name="bar"),
                MockObject(pk=3, name="baz"),
            ]
        )
        self.instance = self.queryset.items[2]
        self.field = PresentablePrimaryKeyRelatedField(
            queryset=self.queryset, presentation_serializer=PresentationSerializer
        )

    def test_representation(self):
        representation = self.field.to_representation(self.instance)
        expected_representation = PresentationSerializer(self.instance).data
        assert representation == expected_representation

    def test_read_source_with_context(self):
        representation = SerializerWithPresentable(self.instance)
        expected_representation = [PresentationSerializer(x).data for x in MockObject().foo_property]
        assert representation.data['test_many_field'] == expected_representation
        assert representation.data['test_function_field'] == expected_representation

        expected_representation = PresentationSerializer(MockObject().bar_property).data
        assert representation.data['test_field'] == expected_representation


class TestPresentableSlugRelatedField(APISimpleTestCase):
    def setUp(self):
        self.queryset = MockQueryset(
            [
                MockObject(pk=1, name="foo"),
                MockObject(pk=2, name="bar"),
                MockObject(pk=3, name="baz"),
            ]
        )
        self.instance = self.queryset.items[2]
        self.field = PresentableSlugRelatedField(
            slug_field="name",
            queryset=self.queryset,
            presentation_serializer=PresentationSerializer,
        )

    def test_representation(self):
        representation = self.field.to_representation(self.instance)
        expected_representation = PresentationSerializer(self.instance).data
        assert representation == expected_representation
