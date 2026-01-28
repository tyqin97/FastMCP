import sqlglot
from rich.console import Console

sql = "SELECT name, age FROM players WHERE age < 23"
tree = sqlglot.parse_one(sql)

Console().print(tree.dump())