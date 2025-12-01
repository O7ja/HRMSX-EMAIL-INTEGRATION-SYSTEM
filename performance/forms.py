from django import forms

from .models import PerformanceReviewCycle, AppreciationRecord, PerformanceReview


class PerformanceReviewCycleForm(forms.ModelForm):
    """Form used by HR to create a new review cycle."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{classes} form-control".strip()

    class Meta:
        model = PerformanceReviewCycle
        fields = [
            'name',
            'start_date',
            'end_date',
            'submission_deadline',
            'self_assessment_link',
            'guidelines',
            'criteria',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'submission_deadline': forms.DateInput(attrs={'type': 'date'}),
            'guidelines': forms.Textarea(attrs={'rows': 4}),
            'criteria': forms.Textarea(attrs={'rows': 4}),
        }


class SelfAssessmentForm(forms.ModelForm):
    """Form for employees to submit their self-assessment."""

    class Meta:
        model = PerformanceReview
        fields = ['self_assessment_submitted']
        widgets = {
            'self_assessment_submitted': forms.HiddenInput(),
        }


class SelfAssessmentSubmissionForm(forms.Form):
    """Form for employees to enter self-assessment content."""

    assessment_content = forms.CharField(
        label='Self-Assessment',
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': 'Describe your accomplishments, challenges, goals, and growth areas during this review period...'}),
        help_text='Please provide a comprehensive self-assessment covering your performance, achievements, and areas for improvement.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assessment_content'].widget.attrs['class'] = 'form-control'


class AppreciationEmailForm(forms.ModelForm):
    """Form for managers to send recognition."""

    cc_team = forms.BooleanField(
        required=False,
        help_text="CC the employee's team members.",
    )
    cc_hr = forms.BooleanField(
        required=False,
        initial=True,
        help_text="CC the HR team for visibility.",
    )

    class Meta:
        model = AppreciationRecord
        fields = ['employee', 'subject', 'message', 'badge_attachment', 'cc_team', 'cc_hr']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{classes} form-control".strip()

