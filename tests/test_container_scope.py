import unittest
from core.container import Container

class TestContainerScope(unittest.TestCase):
    def test_test_scope_restores_state(self):
        container = Container()
        container.register('service', lambda: {'name': 'prod'})
        prod_instance = container.get('service')

        with container.test_scope():
            container.register('service', lambda: {'name': 'test'})
            self.assertEqual(container.get('service')['name'], 'test')

        self.assertIs(container.get('service'), prod_instance)

if __name__ == '__main__':
    unittest.main()
