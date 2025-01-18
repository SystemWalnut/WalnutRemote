import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.joinpath("resources", "site-packages").absolute())
)


from walnut.run import main
