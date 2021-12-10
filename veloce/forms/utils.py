from django import forms


def select_option(form):
    for field in form.fields:
        f = form.fields[field]
        if isinstance(f, forms.ChoiceField) and len(f.choices) and f.choices[0][0] == '':
            f.choices = [('', 'Select')] + f.choices[1:]


def disable_fields(form):
    for field in form.fields:
        form.fields[field].widget.attrs = {'disabled': True}


def display_forms(application, modules):
    show_forms = []
    for model, form in modules:
        instance = model.objects.get(application=application)
        if instance is not None:
            form_instance = form(instance=instance, label_suffix='')
            disable_fields(form_instance)
            show_forms.append(form_instance)
    return show_forms
