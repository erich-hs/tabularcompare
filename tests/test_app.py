from tabularcompare import app
from click.testing import CliRunner

def test_tabularcompare_cli():
    runner = CliRunner()
    result = runner.invoke(app.cli, ["--help"])
    assert result.exit_code == 0