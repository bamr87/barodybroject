from django.views.generic import View

class ModelFieldsMixin(View):
    model = None

    def get_model_fields(self):
        if self.model is None:
                raise ValueError("ModelFieldsMixin requires a 'model' attribute to be defined.")
        fields = self.model._meta.get_fields()
        display_fields = self.model().get_display_fields()
        return fields, display_fields