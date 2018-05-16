from collections import OrderedDict


def reorder_fields():
    def decorator(form):
        original_init = form.__init__

        def init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            original_fields = self.fields
            order = self.field_order
            for key, v in original_fields.items():
                if key not in order:
                    del original_fields[key]
            self.fields = OrderedDict(sorted(original_fields.items(), key=lambda k: order.index(k[0])))

        form.__init__ = init
        return form
    return decorator
