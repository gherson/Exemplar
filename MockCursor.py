import exemplar


class MockCursor:
    """Temporarily hijack real cursor to only /record/ calls to the database during tests."""

    def __init__(self):
        assert exemplar.cursor is not MockCursor  # Disallow redundant mocks.
        self.actual = []  # For unit test comparison with expected value.
        self.real_cursor = exemplar.cursor  # For safe-keeping.

    def execute(self, query, tuple_of_values):
        self.actual.append((query, tuple_of_values))

    def get_actual(self):
        return self.actual

    def restore(self):
        # Doesn't work: assert exemplar.cursor is self, type(exemplar.cursor)  # Disallow redundant restorations.
        exemplar.cursor = self.real_cursor

    def mocking(self, on: int) -> None:
        """
        Allow test module to turn on and off mocking of database calls.
        N.B. This type of testing, i.e., with a MockCursor, doesn't require a database.
        :param on: 0 or 1
        :return:
        """
        if on:
            exemplar.cursor = MockCursor()  # So that exemplar's calls to cursor.execute() append to cursor.actual.
        else:
            self.restore()
