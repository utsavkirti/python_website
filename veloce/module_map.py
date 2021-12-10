from veloce import models, forms, enums

MODULE_MAP = dict((a, list(zip(models.application.MODELS[a], forms.application.FORMS[a]))) for a in models.MODELS)
