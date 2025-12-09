import unittest








from src.chatbot.interfaces import batch








class IsBatchTest(unittest.TestCase):

    def test1(self):
        to_test = batch.is_batch

        args = [{"a": 1, "b": "text", "c": None}]


        #test
        self.assertFalse(to_test(*args))


    def test2(self):
        to_test = batch.is_batch

        args = [[0, 1, 1, 1, 0, 0, 0, 0.5]]


        #test
        self.assertFalse(to_test(*args))


    def test3(self):
        to_test = batch.is_batch

        args = [[[0, 1, 1, 1, 0, 0, 0, 0.5]]]


        #test
        self.assertTrue(to_test(*args))
        

    def test4(self):
        to_test = batch.is_batch

        args = ["49507ebd-de55-528e-afdc-2258dd040d19"]


        #test
        self.assertFalse(to_test(*args))


    def test5(self):
        to_test = batch.is_batch

        args = [["49507ebd-de55-528e-afdc-2258dd040d19"]]


        #test
        self.assertTrue(to_test(*args))


    def test6(self):
        to_test = batch.is_batch

        args = [["this is", "some sort of text", "which should be a batch"]]


        #test
        self.assertFalse(to_test(*args))


    def test7(self):
        to_test = batch.is_batch

        args = [["uuid1", "uuid2", "uuid3"]]


        #test
        self.assertTrue(to_test(*args))








class BatchifyTest(unittest.TestCase):
    
    def test1(self):
        to_test = batch.batchify


        @to_test("x")
        @to_test("y")
        def f(x, y):
            return(x, y)

        self.assertEqual(([1], [2]), f(1, 2))
        # Output: [1] [2]

    def test2(self):
        to_test = batch.batchify


        @to_test("x")
        @to_test("y")
        def f(x, y):
            return(x, y)

        self.assertEqual((["something"], ["something else"]), f("something", "something else"))


    def test3(self):
        to_test = batch.batchify


        @to_test("x", list[str])
        @to_test("y", list[str])
        def f(x, y):
            return(x, y)

        self.assertEqual((["something", "else"], ["something else"]), f(["something", "else"], ["something else"]))


    def test4(self):
        to_test = batch.batchify


        @to_test("x", list[str])
        @to_test("y", list[list[str]])
        def f(x, y):
            return(x, y)

        self.assertEqual((["something", "else"], [["something else"]]), f(["something", "else"], [["something else"]]))









class BatchableTest(unittest.TestCase):

    # -------------------------
    # Hilfsfunktionen (statisch)
    # -------------------------

    @staticmethod
    @batch.batchable()
    def _add_one(x):
        return x + 1

    @staticmethod
    @batch.batchable()
    def _add_xy(x, y):
        return x + y

    @staticmethod
    @batch.batchable()
    def _tuple_xy(x, y):
        return (x, y)

    @staticmethod
    @batch.batchable()
    def _with_optional(x, y=None):
        return (x, y)

    # -------------------------
    # Hilfsklasse für Methodentests
    # -------------------------

    class _MyAdder:
        def __init__(self, bias):
            self.bias = bias

        @batch.batchable()
        def add(self, x):
            return self.bias + x

    # -------------------------
    # weitere Hilfsfunktionen (statisch)
    # -------------------------

    @staticmethod
    @batch.batchable(inherent=True)
    def _inherent_echo(x):
        # soll einfach unverändert durchreichen
        return x

    @staticmethod
    @batch.batchable  # ohne Klammern
    def _no_parens_double(x):
        return x * 2

    # -------------------------
    # Testfälle
    # -------------------------

    def test_no_batch_calls_function_once(self):
        """
        Testet:
        - Wenn KEIN Argument ein Batch ist, wird die Funktion normal ausgeführt.
        - Es findet KEIN Batching statt.

        Erwartung:
        _add_one(1) -> 2
        """
        self.assertEqual(2, self._add_one(1))

    def test_single_batch_argument_is_applied_elementwise(self):
        """
        Testet:
        - Ein einziges Batch-Argument führt zu einer elementweisen Ausführung.
        - Die Funktion wird für jedes Element separat aufgerufen.

        Erwartung:
        [1,2,3] -> [2,3,4]
        """
        b = batch.Batch([1, 2, 3])
        result = self._add_one(b)
        self.assertEqual([2, 3, 4], result)

    def test_multiple_batch_arguments_same_length(self):
        """
        Testet:
        - Mehrere Batch-Argumente mit gleicher Länge werden elementweise
          zusammengeführt (zip).
        - Die Funktion erhält pro Iteration ein Wertepaar.

        Erwartung:
        [1,2,3] + [10,20,30] -> [11,22,33]
        """
        bx = batch.Batch([1, 2, 3])
        by = batch.Batch([10, 20, 30])
        result = self._add_xy(bx, by)
        self.assertEqual([11, 22, 33], result)

    def test_first_non_batch_argument_disables_batching(self):
        """
        Testet:
        - Die Batchgröße wird durch das erste batchbare Argument bestimmt.
        - ABER: Wenn der erste Parameter KEIN Batch ist, wird NICHT gebatcht.
        - Spätere Batch-Argumente bleiben unbearbeitet.

        Erwartung:
        _tuple_xy(1, Batch([...])) -> (1, Batch([...]))
        """
        b = batch.Batch([1, 2, 3])
        result = self._tuple_xy(1, b)
        self.assertEqual((1, b), result)

    def test_none_is_treated_as_scalar_and_does_not_block_batching(self):
        """
        Testet:
        - None gilt als skalare Eingabe.
        - None verhindert Batching NICHT.
        - Batching findet korrekt statt, wenn ein anderes Argument ein Batch ist.

        Erwartung:
        _with_optional([1,2,3]) -> [(1,None),(2,None),(3,None)]
        """
        b = batch.Batch([1, 2, 3])
        result = self._with_optional(b)
        self.assertEqual([(1, None), (2, None), (3, None)], result)

    def test_instance_method_self_is_scalar_and_argument_is_batched(self):
        """
        Testet:
        - Methoden: 'self' muss als SCALAR erkannt werden.
        - Nur die echten Argumente der Methode dürfen gebatcht werden.
        - Batchable funktioniert auch auf Instanzmethoden.

        Erwartung:
        bias=10, Batch([1,2,3]) -> [11,12,13]
        """
        adder = self._MyAdder(10)
        b = batch.Batch([1, 2, 3])
        result = adder.add(b)
        self.assertEqual([11, 12, 13], result)

    def test_inherent_true_disables_batching(self):
        """
        Testet:
        - Bei inherent=True soll überhaupt KEIN Batching stattfinden.
        - Auch wenn Argumente ein Batch darstellen.
        - Rückgabe ist das rohe Batch-Objekt.

        Erwartung:
        _inherent_echo(Batch([...])) -> identisches Batch
        """
        b = batch.Batch([1, 2, 3])
        result = self._inherent_echo(b)
        self.assertIsInstance(result, batch.Batch)
        self.assertEqual(b, result)

    def test_batchable_without_parentheses(self):
        """
        Testet:
        - @batch.batchable ohne Klammern funktioniert wie @batch.batchable().
        - Callable-Shortcut muss korrekt greifen.

        Erwartung:
        [1,2,3] -> [2,4,6]
        """
        b = batch.Batch([1, 2, 3])
        result = self._no_parens_double(b)
        self.assertEqual([2, 4, 6], result)

    def test_empty_batch_returns_empty_list(self):
        """
        Testet:
        - Leere Batches müssen erlaubt sein.
        - Die Ausgabe muss eine leere Liste sein.
        - Die Funktion darf nicht abstürzen oder None zurückgeben.

        Erwartung:
        [] -> []
        """
        b = batch.Batch([])
        result = self._add_one(b)
        self.assertEqual([], result)













    