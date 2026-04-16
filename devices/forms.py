from django import forms
from devices.models import Device, DeviceGroup
from ads.models import Ad


class DeviceForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=DeviceGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign to Groups',
    )

    class Meta:
        model = Device
        fields = ['device_name', 'device_id', 'secret_key', 'location', 'is_online']
        widgets = {
            'device_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter device name'}),
            'device_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique device identifier'}),
            'secret_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Device secret key'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mall Entrance, Floor 2'}),
            'is_online': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()


class DeviceAssignAdsForm(forms.Form):
    ads = forms.ModelMultipleChoiceField(
        queryset=Ad.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Ads',
    )


class DeviceGroupForm(forms.ModelForm):
    class Meta:
        model = DeviceGroup
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mall Floor 1 Displays'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional description', 'rows': 3}),
        }


class DeviceGroupDevicesForm(forms.Form):
    devices = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Devices in Group',
    )


class DeviceGroupAssignAdsForm(forms.Form):
    ads = forms.ModelMultipleChoiceField(
        queryset=Ad.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Ads to Group',
    )
