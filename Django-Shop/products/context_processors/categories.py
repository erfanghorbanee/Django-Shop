from products.models import Category


def categories_processor(request):
    """
    Context processor that adds categories to the context of all templates.
    Returns only active categories, with parent categories and their children.
    """
    # Get all parent categories (categories with no parent)
    parent_categories = Category.objects.filter(
        parent=None, is_active=True
    ).prefetch_related("children")

    # Create a dictionary of parent categories with their children
    categories_hierarchy = {}
    for parent in parent_categories:
        # Get active children for this parent
        children = parent.children.filter(is_active=True)
        if parent.is_active or children.exists():
            categories_hierarchy[parent] = children

    return {"categories_menu": categories_hierarchy}
