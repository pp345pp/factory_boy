# Copyright: See the LICENSE file.

import unittest

from factory import base


class ConstructorModel:
    def __init__(self, **kwargs):
        self.created_via = 'constructor'
        for name, value in kwargs.items():
            setattr(self, name, value)


class ManagerBackedModel:
    def __init__(self, **kwargs):
        self.created_via = 'constructor'
        for name, value in kwargs.items():
            setattr(self, name, value)


class TrackingManager:
    def __init__(self, model_class):
        self.model_class = model_class
        self.create_calls = []
        self.get_or_create_calls = []

    def create(self, **kwargs):
        self.create_calls.append(kwargs)
        instance = self.model_class(**kwargs)
        instance.created_via = 'create'
        return instance

    def get_or_create(self, **kwargs):
        self.get_or_create_calls.append(kwargs)
        instance = self.model_class(**kwargs)
        instance.created_via = 'get_or_create'
        return instance, True


class CreateMethodTests(unittest.TestCase):
    def setUp(self):
        super().setUp()
        ManagerBackedModel.objects = TrackingManager(ManagerBackedModel)

    def test_default_create_method_keeps_constructor_behavior_without_manager(self):
        class ConstructorFactory(base.Factory):
            class Meta:
                model = ConstructorModel

            one = 'one'

        instance = ConstructorFactory.create()

        self.assertEqual('constructor', instance.created_via)
        self.assertEqual('create', ConstructorFactory._meta.create_method)
        self.assertEqual('create', ConstructorFactory.__create_method__)

    def test_create_method_uses_manager_create(self):
        class CreateFactory(base.Factory):
            class Meta:
                model = ManagerBackedModel
                create_method = 'create'

            one = 'one'

        instance = CreateFactory.create()

        self.assertEqual('create', instance.created_via)
        self.assertEqual([{'one': 'one'}], ManagerBackedModel.objects.create_calls)
        self.assertEqual([], ManagerBackedModel.objects.get_or_create_calls)
        self.assertEqual('create', CreateFactory.__create_method__)

    def test_get_or_create_method_returns_instance(self):
        class GetOrCreateFactory(base.Factory):
            class Meta:
                model = ManagerBackedModel
                create_method = 'get_or_create'

            one = 'one'

        instance = GetOrCreateFactory.create()

        self.assertEqual('get_or_create', instance.created_via)
        self.assertEqual([], ManagerBackedModel.objects.create_calls)
        self.assertEqual([{'one': 'one'}], ManagerBackedModel.objects.get_or_create_calls)
        self.assertEqual('get_or_create', GetOrCreateFactory.__create_method__)

    def test_callable_create_method_is_used_directly(self):
        calls = []

        def create_method(*args, **kwargs):
            calls.append((args, kwargs))
            instance = ManagerBackedModel(**kwargs)
            instance.created_via = 'callable'
            return instance

        meta = type('Meta', (), {
            'model': ManagerBackedModel,
            'create_method': create_method,
        })
        CallableFactory = type('CallableFactory', (base.Factory,), {
            'Meta': meta,
            'one': 'one',
        })

        instance = CallableFactory.create()

        self.assertEqual('callable', instance.created_via)
        self.assertEqual([((), {'one': 'one'})], calls)
        self.assertEqual([], ManagerBackedModel.objects.create_calls)
        self.assertEqual([], ManagerBackedModel.objects.get_or_create_calls)
        self.assertIs(create_method, CallableFactory.__create_method__)
