from walnut.run import main
import sys
from pathlib import Path

sys.path.insert(
    0, Path(__file__).parent.joinpath("resources", "site-packages").absolute()
)
