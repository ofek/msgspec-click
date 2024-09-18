# SPDX-FileCopyrightText: 2024-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import click
from msgspec import NODEFAULT, inspect

if TYPE_CHECKING:
    from collections.abc import Callable

    import msgspec

SUPPORTED_UNION_LENGTH = 2


def generate_options(struct: type[msgspec.Struct]) -> list[click.Option]:
    """
    Parameters:
        struct: The [msgspec.Struct][] type with which to generate options.

    Returns:
        A list of [click.Option][] instances.
    """
    struct_info = cast(inspect.StructType, inspect.type_info(struct))

    options: list[click.Option] = []
    for field in struct_info.fields:
        name = field.encode_name
        default = field.default
        params: list[str] = []
        settings: dict[str, Any] = {}

        if isinstance(field.type, inspect.Metadata):
            field_type = field.type.type
            extra: dict[str, Any] | None = field.type.extra
            if extra is not None:
                params.extend(extra.pop('params', []))
                settings.update(extra)
        else:
            field_type = field.type

        if isinstance(field_type, inspect.UnionType):
            if len(field_type.types) != SUPPORTED_UNION_LENGTH or not isinstance(field_type.types[1], inspect.NoneType):
                message = f'Only `TYPE_DEF | None` union types are supported for field `{name}`: {field_type}'
                raise TypeError(message)

            field_type = field_type.types[0]
            default = None

        name_flag = f'--{name}'.replace('_', '-')
        if not params:
            params.append(name_flag)
        elif params[-1] != name and name_flag not in params:
            params.append(name)

        if field.required:
            settings['required'] = True
        elif 'default' not in settings and field.default is not NODEFAULT:
            settings['default'] = default

        ftype = type(field_type)
        if ftype not in SETTERS:
            message = f'Unsupported type for field `{name}`: {ftype}'
            raise TypeError(message)

        setter = SETTERS[ftype]
        try:
            setter(settings, field_type)
        except Exception as e:  # noqa: BLE001
            message = f'Error generating option for field `{name}`, {e}'
            raise TypeError(message) from None

        option_class = settings.pop('cls', click.Option)
        option = option_class(params, **settings)
        options.append(option)

    return options


def _set_str(
    settings: dict[str, Any],  # noqa: ARG001
    field_type: inspect.Type,
) -> None:
    assert isinstance(field_type, inspect.StrType)  # noqa: S101


def _set_bool(
    settings: dict[str, Any],
    field_type: inspect.Type,
) -> None:
    assert isinstance(field_type, inspect.BoolType)  # noqa: S101

    settings['is_flag'] = True


def _set_int(
    settings: dict[str, Any],
    field_type: inspect.Type,
) -> None:
    assert isinstance(field_type, inspect.IntType)  # noqa: S101

    if not settings.get('count', False):
        settings['type'] = int
    elif not isinstance(settings.get('default', []), list):
        settings['default'] = []


def _set_float(
    settings: dict[str, Any],
    field_type: inspect.Type,
) -> None:
    assert isinstance(field_type, inspect.FloatType)  # noqa: S101

    settings['type'] = float


def _set_list(settings: dict[str, Any], field_type: inspect.Type) -> None:
    assert isinstance(field_type, inspect.ListType)  # noqa: S101

    item_type = field_type.item_type
    itype = type(item_type)
    click_type: click.ParamType
    if itype in {inspect.StrType, inspect.AnyType}:
        click_type = click.STRING
    elif itype is inspect.IntType:
        click_type = click.INT
    elif itype is inspect.FloatType:
        click_type = click.FLOAT
    elif itype is inspect.BoolType:
        click_type = click.BOOL
    else:
        message = f'type of item is unsupported: {itype}'
        raise TypeError(message)

    settings['cls'] = ListOption
    settings['type'] = ListParamType(click_type)
    if 'nargs' not in settings:
        settings['multiple'] = True


def _set_tuple(settings: dict[str, Any], field_type: inspect.Type) -> None:
    assert isinstance(field_type, inspect.TupleType)  # noqa: S101

    param_types: list[click.ParamType] = []
    for i, item_type in enumerate(field_type.item_types, 1):
        itype = type(item_type)
        if itype in {inspect.StrType, inspect.AnyType}:
            param_types.append(click.STRING)
        elif itype is inspect.IntType:
            param_types.append(click.INT)
        elif itype is inspect.FloatType:
            param_types.append(click.FLOAT)
        elif itype is inspect.BoolType:
            param_types.append(click.BOOL)
        else:
            message = f'type of item #{i} is unsupported: {itype}'
            raise TypeError(message)

    settings['type'] = click.Tuple(param_types)
    settings['nargs'] = len(param_types)


def _set_var_tuple(settings: dict[str, Any], field_type: inspect.Type) -> None:
    assert isinstance(field_type, inspect.VarTupleType)  # noqa: S101

    if 'nargs' not in settings:
        message = '`nargs` is required'
        raise ValueError(message)

    nargs = settings['nargs']
    if len(settings.get('default', ())) != nargs:
        message = f'default value must be of length `nargs`: {nargs}'
        raise ValueError(message)

    itype = type(field_type.item_type)
    click_type: click.ParamType
    if itype in {inspect.StrType, inspect.AnyType}:
        click_type = click.STRING
    elif itype is inspect.IntType:
        click_type = click.INT
    elif itype is inspect.FloatType:
        click_type = click.FLOAT
    elif itype is inspect.BoolType:
        click_type = click.BOOL
    else:
        message = f'type of item is unsupported: {itype}'
        raise TypeError(message)

    settings['type'] = click.Tuple([click_type for _ in range(nargs)])


def _set_literal(settings: dict[str, Any], field_type: inspect.Type) -> None:
    assert isinstance(field_type, inspect.LiteralType)  # noqa: S101

    choices: list[str] = []
    for value in field_type.values:
        if isinstance(value, str):
            choices.append(value)
        else:
            message = 'only `str` literals are supported'
            raise TypeError(message)

    settings['type'] = click.Choice(tuple(choices))


class ListOption(click.Option):
    def type_cast_value(self, ctx: click.Context, value: Any) -> list[Any]:  # no cov
        return list(super().type_cast_value(ctx, value))


class ListParamType(click.ParamType):
    name = 'List'

    def __init__(self, item_type: click.ParamType):
        self._item_type = item_type

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> Any:  # no cov
        return self._item_type(value, param, ctx)


SETTERS: dict[type[inspect.Type], Callable[[dict[str, Any], inspect.Type], None]] = {
    inspect.BoolType: _set_bool,
    inspect.FloatType: _set_float,
    inspect.IntType: _set_int,
    inspect.ListType: _set_list,
    inspect.LiteralType: _set_literal,
    inspect.StrType: _set_str,
    inspect.TupleType: _set_tuple,
    inspect.VarTupleType: _set_var_tuple,
}
