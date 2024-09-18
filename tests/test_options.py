# SPDX-FileCopyrightText: 2024-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import Annotated, Any, Literal, Union

import pytest
from msgspec import Meta, Struct

from msgspec_click import generate_options


def test_unsupported_type() -> None:
    class Example(Struct):
        field: set

    with pytest.raises(TypeError, match='^Unsupported type for field `field`: '):
        generate_options(Example)


class TestMetadata:
    def test_full(self) -> None:
        class Example(Struct):
            field: Annotated[str, Meta(extra={'help': 'This is a string field', 'params': ['-f', '--field']})] = ''

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': '',
            'envvar': None,
            'flag_value': True,
            'help': 'This is a string field',
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['-f', '--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'text', 'param_type': 'String'},
        }

    def test_partial(self) -> None:
        # This test is purely to satisfy code coverage but does not represent real usage
        class Example(Struct):
            field: Annotated[str, Meta(description='foo')] = ''

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': '',
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'text', 'param_type': 'String'},
        }

    def test_field_name(self) -> None:
        class Example(Struct):
            field: Annotated[str, Meta(extra={'params': ['-f']})] = ''

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': '',
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['-f'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'text', 'param_type': 'String'},
        }


class TestStr:
    def test_required(self) -> None:
        class Example(Struct):
            field: str

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': True,
            'secondary_opts': [],
            'type': {'name': 'text', 'param_type': 'String'},
        }

    def test_not_required(self) -> None:
        class Example(Struct):
            field: str = ''

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': '',
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'text', 'param_type': 'String'},
        }


class TestBool:
    def test(self) -> None:
        class Example(Struct):
            field: bool = False

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': False,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': True,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'boolean', 'param_type': 'Bool'},
        }


class TestInt:
    def test_basic(self) -> None:
        class Example(Struct):
            field: int = 0

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': 0,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'integer', 'param_type': 'Int'},
        }

    def test_count(self) -> None:
        class Example(Struct):
            field: Annotated[int, Meta(extra={'count': True})] = 0

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': True,
            'default': [],
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'clamp': False,
                'max': None,
                'max_open': False,
                'min': 0,
                'min_open': False,
                'name': 'integer range',
                'param_type': 'IntRange',
            },
        }

    def test_count_default(self) -> None:
        class Example(Struct):
            field: Annotated[int, Meta(extra={'count': True, 'default': []})] = 0

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': True,
            'default': [],
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'clamp': False,
                'max': None,
                'max_open': False,
                'min': 0,
                'min_open': False,
                'name': 'integer range',
                'param_type': 'IntRange',
            },
        }


class TestFloat:
    def test(self) -> None:
        class Example(Struct):
            field: float = 0.0

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': 0.0,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'float', 'param_type': 'Float'},
        }


class TestUnion:
    def test_unsupported_union(self) -> None:
        class Example(Struct):
            field: Union[str, int, None] = None  # noqa: UP007

        with pytest.raises(
            TypeError,
            match=r'^Only `TYPE_DEF \| None` union types are supported for field `field`: UnionType',
        ):
            generate_options(Example)

    def test_no_none_type(self) -> None:
        class Example(Struct):
            field: Union[str, int] = 0  # noqa: UP007

        with pytest.raises(
            TypeError,
            match=r'^Only `TYPE_DEF \| None` union types are supported for field `field`: UnionType',
        ):
            generate_options(Example)

    def test_str(self) -> None:
        class Example(Struct):
            field: Union[str, None] = None  # noqa: UP007

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'text', 'param_type': 'String'},
        }


class TestList:
    def test_unsupported_item_type(self) -> None:
        class Example(Struct):
            field: list[set] = []

        with pytest.raises(
            TypeError,
            match=r'^Error generating option for field `field`, type of item is unsupported:',
        ):
            generate_options(Example)

    def test_untyped(self) -> None:
        class Example(Struct):
            field: list = []

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': True,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'List', 'param_type': 'List'},
        }

    def test_nargs(self) -> None:
        class Example(Struct):
            field: Annotated[list, Meta(extra={'nargs': 2})] = []

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'List', 'param_type': 'List'},
        }

    def test_str(self) -> None:
        class Example(Struct):
            field: list[str] = []

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': True,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'List', 'param_type': 'List'},
        }

    def test_int(self) -> None:
        class Example(Struct):
            field: list[int] = []

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': True,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'List', 'param_type': 'List'},
        }

    def test_float(self) -> None:
        class Example(Struct):
            field: list[float] = []

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': True,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'List', 'param_type': 'List'},
        }

    def test_bool(self) -> None:
        class Example(Struct):
            field: list[bool] = []

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': True,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {'name': 'List', 'param_type': 'List'},
        }


class TestTuple:
    def test_unsupported_item_type(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[set, set], Meta(extra={'nargs': 2})] = (set(), set())

        with pytest.raises(
            TypeError, match=r'^Error generating option for field `field`, type of item #1 is unsupported:'
        ):
            generate_options(Example)

    def test_any(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[Any, Any], Meta(extra={'nargs': 2})] = ('foo', 'bar')

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': ('foo', 'bar'),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<text text>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                ],
            },
        }

    def test_str(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[str, str], Meta(extra={'nargs': 2})] = ('foo', 'bar')

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': ('foo', 'bar'),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<text text>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                ],
            },
        }

    def test_int(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[int, int], Meta(extra={'nargs': 2})] = (9000, 42)

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': (9000, 42),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<integer integer>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'integer',
                        'param_type': 'Int',
                    },
                    {
                        'name': 'integer',
                        'param_type': 'Int',
                    },
                ],
            },
        }

    def test_float(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[float, float], Meta(extra={'nargs': 2})] = (3.14, 9.8)

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': (3.14, 9.8),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<float float>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'float',
                        'param_type': 'Float',
                    },
                    {
                        'name': 'float',
                        'param_type': 'Float',
                    },
                ],
            },
        }

    def test_bool(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[bool, bool], Meta(extra={'nargs': 2})] = (True, False)

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': (True, False),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<boolean boolean>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'boolean',
                        'param_type': 'Bool',
                    },
                    {
                        'name': 'boolean',
                        'param_type': 'Bool',
                    },
                ],
            },
        }

    def test_mixed(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[Any, str, int, float, bool], Meta(extra={'nargs': 5})] = (
                'foo',
                'bar',
                42,
                3.14,
                True,
            )

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': ('foo', 'bar', 42, 3.14, True),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 5,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<text text integer float boolean>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                    {
                        'name': 'integer',
                        'param_type': 'Int',
                    },
                    {
                        'name': 'float',
                        'param_type': 'Float',
                    },
                    {
                        'name': 'boolean',
                        'param_type': 'Bool',
                    },
                ],
            },
        }

    def test_union_none(self) -> None:
        class Example(Struct):
            field: Annotated[Union[tuple[Any, Any], None], Meta(extra={'nargs': 2})] = None  # noqa: UP007

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': None,
            'envvar': None,
            'flag_value': True,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<text text>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                ],
            },
        }


class TestVarTuple:
    def test_no_nargs(self) -> None:
        class Example(Struct):
            field: tuple = ()

        with pytest.raises(
            TypeError,
            match=r'^Error generating option for field `field`, `nargs` is required$',
        ):
            generate_options(Example)

    def test_default_incorrect_length(self) -> None:
        class Example(Struct):
            field: Annotated[tuple, Meta(extra={'nargs': 2})] = ()

        with pytest.raises(
            TypeError,
            match=r'^Error generating option for field `field`, default value must be of length `nargs`: 2$',
        ):
            generate_options(Example)

    def test_unsupported_item_type(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[set, ...], Meta(extra={'nargs': 2})] = (set(), set())

        with pytest.raises(
            TypeError, match=r'^Error generating option for field `field`, type of item is unsupported:'
        ):
            generate_options(Example)

    def test_untyped(self) -> None:
        class Example(Struct):
            field: Annotated[tuple, Meta(extra={'nargs': 2})] = ('foo', 'bar')

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': ('foo', 'bar'),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<text text>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                ],
            },
        }

    def test_str(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[str, ...], Meta(extra={'nargs': 2})] = ('foo', 'bar')

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': ('foo', 'bar'),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<text text>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                    {
                        'name': 'text',
                        'param_type': 'String',
                    },
                ],
            },
        }

    def test_int(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[int, ...], Meta(extra={'nargs': 2})] = (9000, 42)

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': (9000, 42),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<integer integer>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'integer',
                        'param_type': 'Int',
                    },
                    {
                        'name': 'integer',
                        'param_type': 'Int',
                    },
                ],
            },
        }

    def test_float(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[float, ...], Meta(extra={'nargs': 2})] = (3.14, 9.8)

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': (3.14, 9.8),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<float float>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'float',
                        'param_type': 'Float',
                    },
                    {
                        'name': 'float',
                        'param_type': 'Float',
                    },
                ],
            },
        }

    def test_bool(self) -> None:
        class Example(Struct):
            field: Annotated[tuple[bool, ...], Meta(extra={'nargs': 2})] = (True, False)

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': (True, False),
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 2,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'name': '<boolean boolean>',
                'param_type': 'Tuple',
                'types': [
                    {
                        'name': 'boolean',
                        'param_type': 'Bool',
                    },
                    {
                        'name': 'boolean',
                        'param_type': 'Bool',
                    },
                ],
            },
        }


class TestLiteral:
    def test_unsupported_item_type(self) -> None:
        class Example(Struct):
            field: Literal[1, 2] = 1

        with pytest.raises(
            TypeError, match=r'^Error generating option for field `field`, only `str` literals are supported$'
        ):
            generate_options(Example)

    def test_str(self) -> None:
        class Example(Struct):
            field: Literal['foo', 'bar'] = 'foo'

        options = generate_options(Example)
        assert len(options) == 1
        assert options[0].to_info_dict() == {
            'count': False,
            'default': 'foo',
            'envvar': None,
            'flag_value': False,
            'help': None,
            'hidden': False,
            'is_flag': False,
            'multiple': False,
            'name': 'field',
            'nargs': 1,
            'opts': ['--field'],
            'param_type_name': 'option',
            'prompt': None,
            'required': False,
            'secondary_opts': [],
            'type': {
                'case_sensitive': True,
                'choices': (
                    'bar',
                    'foo',
                ),
                'name': 'choice',
                'param_type': 'Choice',
            },
        }
