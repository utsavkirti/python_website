from django import forms
from django.utils.safestring import mark_safe
from datetime import date

MONTHS = [
    (i, date(2020, i, 1).strftime('%B')) for i in range(1, 13)
]


class CustomCheckbox(forms.widgets.CheckboxInput):

    def __init__(self, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label

    def render(self, name, attrs=None, **kwargs):
        attrs = ' '.join([f'{k}="{attrs[k]}"' for k in attrs])
        attrs += ' '.join([f'{k}="{self.attrs[k]}"' for k in self.attrs])

        return mark_safe(f"""
        <label class="checkbox-container">
            {self.label}
            <input type="checkbox" name="{name}" {attrs}>
            <span class="checkmark"></span>
        </label>
        """)


class CustomDate(forms.widgets.DateInput):

    def __init__(self, years, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.years = years

    def render(self, name, attrs=None, **kwargs):
        attrs = ' '.join([f'{k}="{attrs[k]}"' for k in attrs])
        if 'value' in kwargs:
            attrs += ' ' + f"value=\"{kwargs['value']}\""
        attrs += ' '.join([f'{k}="{self.attrs[k]}"' for k in self.attrs])
        return mark_safe(f"""<input type="date" name="{name}" {attrs}>""")


class CustomFileInput(forms.widgets.FileInput):

    def render(self, name, value, attrs=None, **kwargs):
        filename = value.name.split('/')[-1] if value else None
        attrs['required'] = True if filename is None and attrs.get(
            'required', False) else False
        if not attrs['required']:
            del attrs['required']
        attrs = ' '.join([f'{k}="{attrs[k]}"' for k in attrs])
        attrs += ' '.join([f'{k}="{self.attrs[k]}"' for k in self.attrs])
        current = f"""
            <div style="padding: 0px 10px">
                Currently set to <a href="/download?path={value}" target="_blank">{filename}</a>.
            </div>
        """

        return mark_safe(f"""
            <div style="display: flex; flex-direction: column;">
                { current if value is not None else '' }
                <div style="display:flex">
                    <input type="file" name="{name}" id="id_{name}" {attrs}>
                    </input>
                </div>
            </div>
        """)
