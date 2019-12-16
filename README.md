# Kawatta

## Introduction

Allows you to get a human readable log of the changes between two Python structures

## Installation

You just have to clone this repository and install it using the command
```bash
pip install .
```

Or you can also install it from PyPi
```bash
pip install kawatta
```

You can test your installation with the following command :

```bash
python -c "import kawatta; kawatta.compare({1: 2}, {1: 3}, kawatta.HumanReadableLogsCallbacks()).print_log()"
```

It should display the following result :
```
[~] 1 : 2 => 3
```

## Usage

Here is a basic example to get you started :

```python
callbacks = kawatta.HumanReadableLogsCallbacks()
kawatta.compare({1: 2, 3: 4}, {1: 3}, callbacks)
callbacks.print_log()
```

It should print the following result :
```python
[~] 1 : 2 => 3
[-] 3 = 4
```

## Licensing

Kawatta uses the MIT license, you can find more details about it [here](LICENSE)

## Contributing

You can find more details about contributions [here](CONTRIBUTING.md)