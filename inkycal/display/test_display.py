from unittest import TestCase

from inkycal.display import Display


class TestDisplay(TestCase):

    # def setUp(self) -> None:
    #     self.display = Display()

    def test_get_display_names(self):

        fetched_displays = Display.get_display_names()
        assert len(fetched_displays) >1
        assert isinstance(fetched_displays, list)