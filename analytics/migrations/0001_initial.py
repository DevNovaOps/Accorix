# Generated migration for analytics app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('document_type', models.CharField(choices=[('invoice', 'Invoice'), ('bill', 'Bill'), ('receipt', 'Receipt'), ('statement', 'Statement'), ('other', 'Other')], default='other', max_length=20)),
                ('pdf_file', models.FileField(upload_to='documents/%Y/%m/')),
                ('extracted_text', models.TextField(blank=True, help_text='Extracted text from PDF')),
                ('extracted_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('extracted_date', models.DateField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('processed', models.BooleanField(default=False)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='AnalyticsReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('report_type', models.CharField(choices=[('revenue', 'Revenue Analysis'), ('expense', 'Expense Analysis'), ('profit_loss', 'Profit & Loss'), ('cash_flow', 'Cash Flow'), ('budget_variance', 'Budget Variance'), ('customer_analysis', 'Customer Analysis'), ('vendor_analysis', 'Vendor Analysis')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('chart_image', models.ImageField(blank=True, null=True, upload_to='charts/%Y/%m/')),
                ('data_json', models.JSONField(default=dict, help_text='Chart data in JSON format')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('generated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generated_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
    ]