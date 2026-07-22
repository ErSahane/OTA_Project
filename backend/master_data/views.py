from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from accounts.permissions import IsStaffOrAdmin
from .import_export import ImportExportService


class ImportExportViewSet(ViewSet):
    permission_classes = [IsStaffOrAdmin]

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        model_name = request.query_params.get("model")
        if not model_name:
            return Response({"detail": "model is required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"csv": ImportExportService.export_csv(model_name)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="import")
    def import_data(self, request):
        model_name = request.data.get("model")
        csv_data = request.data.get("csv")
        if not model_name or not csv_data:
            return Response({"detail": "model and csv are required"}, status=status.HTTP_400_BAD_REQUEST)
        count = ImportExportService.import_csv(model_name, csv_data)
        return Response({"imported": count}, status=status.HTTP_200_OK)
