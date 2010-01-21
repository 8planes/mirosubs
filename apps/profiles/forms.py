from django import forms
from profiles.models import Profile

class EditProfileForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password_verify = forms.CharField(widget=forms.PasswordInput,
                                          required=False,
                                          label='Confirm new password:')
    
    class Meta:
        model = Profile
        exclude = ('user',)

    def clean(self):
        current, new, verify = map(self.cleaned_data.get,
                    ('current_password', 'new_password', 'new_password_verify'))
        if current and not self.instance.user.check_password(current):
            raise forms.ValidationError('Invalid password.')
        if new and new != verify:
            raise forms.ValidationError('The two passwords did not match.')
        return self.cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data.get('new_password')
        if password:
            self.instance.user.set_password(password)
        return super(EditProfileForm, self).save(commit)
        