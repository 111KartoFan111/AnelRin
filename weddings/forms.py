from django import forms
from .models import Wedding, Task, CartItem


class WeddingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Выберите дату свадьбы'
    )

    class Meta:
        model = Wedding
        fields = ['date', 'style', 'location', 'guests_count', 'budget']
        widgets = {
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
        }


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Срок выполнения задачи'
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority']


class TaskFilterForm(forms.Form):
    FILTER_CHOICES = [
        ('all', 'Все задачи'),
        ('completed', 'Выполненные'),
        ('pending', 'Невыполненные'),
        ('overdue', 'Просроченные'),
    ]

    filter_by = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ProductFilterForm(forms.Form):
    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Мин. цена', 'class': 'form-control'})
    )

    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Макс. цена', 'class': 'form-control'})
    )
    style = forms.ChoiceField(
        choices=[('', 'Все стили')] + Wedding.STYLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super(ProductFilterForm, self).__init__(*args, **kwargs)
        if categories:
            category_choices = [('', 'Все категории')]
            for category in categories:
                category_choices.append((category.id, category.name))
            self.fields['category'].choices = category_choices