from django.shortcuts import get_object_or_404


class CheckParentPermissionMixin:
    # https://github.com/alanjds/drf-nested-routers/issues/73#issuecomment-944256853

    def __init__(self, **kwargs):
        self.parent_obj = None
        super().__init__(**kwargs)

    def check_permissions(self, request):
        super().check_permissions(request)

        # check permissions for the parent object
        parent_lookup_url_kwarg = self.parent_lookup_url_kwarg or self.parent_lookup_field
        filter_kwargs = {
            self.parent_lookup_field: self.kwargs[parent_lookup_url_kwarg]
        }
        
        self.parent_obj = get_object_or_404(self.parent_queryset, **filter_kwargs)
        self.parent_obj._is_parent_obj = True
        super().check_object_permissions(request, self.parent_obj)
