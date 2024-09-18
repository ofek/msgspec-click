# Usage

-----

## Example

Here, we illustrate how to use the [`generate_options`][msgspec_click.generate_options] function on a [`msgspec.Struct`][] type. The [`click.Option`][] instances it generates produce values that may be used to instantiate the type.

=== ":octicons-file-code-16: script.py"
    ```python
    from __future__ import annotations

    from typing import Annotated

    import click
    from msgspec import Meta, Struct
    from msgspec_click import generate_options


    class Connection(Struct):
        user: Annotated[
            str,
            Meta(
                extra={
                    "help": "The user's name",
                    "params": ["-u", "--user"],
                }
            )
        ] = ""
        password: Annotated[
            str,
            Meta(
                extra={
                    "help": "The user's password",
                    "params": ["-p", "--pass"],
                    "prompt": True,
                    "hide_input": True,
                    "confirmation_prompt": True,
                }
            )
        ] = ""
        headers: Annotated[list[str], Meta(extra={"params": ["-H"]})] = []
        timeout: float = 10.0
        allow_insecure: bool = False


    @click.command()
    def command(**kwargs) -> None:
        connection = Connection(**kwargs)
        print(connection)


    command.params.extend(generate_options(Connection))
    command()
    ```

You can view the help text like so:

```console
$ python script.py --help
Usage: script.py [OPTIONS]

Options:
  -u, --user TEXT   The user's name
  -p, --pass TEXT   The user's password
  -H LIST
  --timeout FLOAT
  --allow-insecure
  --help            Show this message and exit.
```

Running the script with `secret` as the password produces the following output:

```console
$ python script.py --user alice -H "Key: Value"
Password []:
Repeat for confirmation:
Connection(user='alice', password='secret', headers=['Key: Value'], timeout=10.0, allow_insecure=False)
```

## How it works

The [type](#supported-types) of each field is used to determine the appropriate type of the associated option. Types may be annotated with a [`msgspec.Meta`][] instance to configure the option. All keys in the `extra` dictionary are passed directly to the [`click.Option`][] constructor as keyword arguments, except for the `params` key which is extracted and passed as an argument.

If the `params` key is not set, then the name of the field is used as the only option parameter e.g. `some_field` would become `--some-field`. If the key is set but does not contain the expected flag name nor does it contain the field name, then the field name is appended to the list of parameters to force Click to use the field name as the option name without interfering with the chosen parameters.

If the `default` key is set then it is used as the default value for the option with a fallback to the default value of the field. If a field has no default value, then `required` is set to `True` for the option.

## Supported types

### Primitive types

| Type | Behavior |
| --- | --- |
| [`str`][] | N/A |
| [`bool`][] | The `is_flag` key is set to `True`. |
| [`int`][] | If the `count` key is not set to `True` then the `type` key is set to `int`. Otherwise, the `default` key is set to `[]` to satisfy what Click expects for such repeatable options like `-vvv`. |
| [`float`][] | The `type` key is set to `float`. |

### Collection types

| Type | Behavior |
| --- | --- |
| [`list`][] | The `type` is set to a [`click.Option`][] subclass that only converts the final value to the proper type. If the `nargs` setting is not defined then `multiple` will be set to `True`. All of the [primitive types](#primitive-types) are supported as items. If the item type is not defined or is [`typing.Any`][] then the type is considered [`str`][]. |
| [`tuple`][] | Both standard and variadic forms are supported. If the standard form (e.g. `tuple[str, int]`) is used then the `type` key is set to [`click.Tuple`][] and `nargs` is set to the number of items. If the variadic form (e.g. `tuple[str, ...]`) is used then the `type` key is set to [`click.Tuple`][], and the `nargs` key must already be defined. All of the [primitive types](#primitive-types) are supported as items. If an item type is not defined or is [`typing.Any`][] then the type is considered [`str`][]. |

### Complex types

| Type | Behavior |
| --- | --- |
| [`Union`][typing.Union] | Only `TYPE_DEF | None` union types are supported i.e. exactly 2 types with the final being `None`. This is to allow the default value being `None` for easily checking if options were set by the user. The first type may be any supported type except another union. |
| [`Literal`][typing.Literal] | The `type` key is set to [`click.Choice`][] with the literal's values. Only [`str`][] literals are supported. |

## Caveats

Type annotations that are not supported by the Python version at runtime will not work. For example, subscripting built-in types like `list[int]` became supported in Python 3.9 and using the `|` operator for unions became supported in Python 3.10.

Although `from __future__ import annotations` may hide these runtime errors due to postponed evaluation of annotations, it does not change the supported syntax of the interpreter.
