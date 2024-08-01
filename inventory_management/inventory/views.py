from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, InventoryItemForm
from .models import InventoryItem, Category
from inventory_management.settings import LOW_QUANTITY
from django.contrib import messages

class Index(TemplateView):
    template_name = 'inventory/index.html'

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        category_id = request.GET.get('category')
        if category_id:
            items = InventoryItem.objects.filter(user=self.request.user.id, category_id=category_id).order_by('id')
        else:
            items = InventoryItem.objects.filter(user=self.request.user.id).order_by('id')

        low_inventory = InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte=LOW_QUANTITY
        )

        if low_inventory.count() > 0:
            if low_inventory.count() > 1:
                messages.error(request, f'{low_inventory.count()} items have low inventory')
            else:
                messages.error(request, f'{low_inventory.count()} item has low inventory')

        low_inventory_ids = InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte=LOW_QUANTITY
        ).values_list('id', flat=True)

        categories = Category.objects.all()

        return render(request, 'inventory/dashboard.html', {'items': items, 'low_inventory_ids': low_inventory_ids, 'categories': categories})

class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )

            login(request, user)
            return redirect('index')

        return render(request, 'inventory/signup.html', {'form': form})
		
class SearchItemView(View):
    def get(self, request):
        barcode = request.GET.get('barcode')
        item = None
        
        if barcode:
            item = get_object_or_404(InventoryItem, barcode=barcode)
        
        return render(request, 'inventory/search_item.html', {'item': item})

class UpdateItemView(View):
    def get(self, request):
        barcode = request.GET.get('barcode')
        item = None
        form = None
        
        if barcode:
            item = get_object_or_404(InventoryItem, barcode=barcode)
            form = InventoryItemForm(instance=item)
        else:
            form = InventoryItemForm()

        return render(request, 'inventory/update_item.html', {'form': form, 'item': item})

    def post(self, request):
        barcode = request.POST.get('barcode')
        item = get_object_or_404(InventoryItem, barcode=barcode)
        form = InventoryItemForm(request.POST, instance=item)
        
        if form.is_valid():
            updated_item = form.save(commit=False)
            action = request.POST.get('action')
            quantity_change = int(request.POST.get('quantity_change', 0))
            
            if action == 'add':
                updated_item.quantity += quantity_change
            elif action == 'delete':
                updated_item.quantity -= quantity_change
            
            updated_item.save()
            return redirect('dashboard')
        
        return render(request, 'inventory/update_item.html', {'form': form, 'item': item})

class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

class DeleteItem(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/delete_item.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'item'
