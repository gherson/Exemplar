import exemplar


class MockCursor:
    """Temporarily hijack real cursor to only record calls to the database (for use by unittest).
    Created 2019-03-27 George Herson"""

    def __init__(self):
        assert exemplar.cursor is not MockCursor  # Disallow redundant mocks.
        self.actual = []  # For unit test comparison with expected value.
        self.real_cursor = exemplar.cursor  # For assignment (back to exemplar.cursor) by .restore() later.

    def execute(self, query, tuple_of_values):
        self.actual.append((query, tuple_of_values))

    def get_actual(self):
        return self.actual

    def restore(self):
        # Doesn't work:  assert exemplar.cursor is self, type(exemplar.cursor)  # Disallow redundant restorations.
        exemplar.cursor = self.real_cursor

    def mocking(self, on: int) -> None:
        """
        To allow caller to turn db mocking on/off.
        N.B. Testing with a MockCursor doesn't require a database.
        :param on: Boolean
        :return:
        """
        if on:
            exemplar.cursor = MockCursor()  # Exemplar's calls to cursor.execute() now append to MockCursor.actual.
        else:
            self.restore()
