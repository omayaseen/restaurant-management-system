from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """
    Collects delivery/contact details for an order at checkout time.

    This is a ModelForm bound to Order, but note that in Step 1 we never
    call form.save() - we only use form.cleaned_data. The actual Order
    row is created later (Step 2), once payment succeeds.
    """

    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'delivery_address', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'full_name': 'Full Name',
            'phone': 'Phone Number',
            'delivery_address': 'Delivery Address',
            'notes': 'Order Notes (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            field.widget.attrs.setdefault(
                'placeholder',
                self.fields[name].label
            )
