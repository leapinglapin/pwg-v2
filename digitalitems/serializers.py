from rest_framework import serializers

from digitalitems.models import DIFile, DownloadHistory, Downloadable, UserDownloadableHistory, DigitalItem
from shop.serializers import ItemSerializer


class DIFileSerializer(serializers.ModelSerializer):
    upload_date = serializers.DateTimeField(format=None)
    last_download_date = serializers.SerializerMethodField()

    class Meta:
        model = DIFile
        fields = ['clean_name', 'id', 'upload_date', 'last_download_date', 'file_size']

    def get_last_download_date(self, file):
        user = self.context.get('user')
        if user and user.is_authenticated:
            try:
                return file.download_history.filter(user=user).latest().timestamp
            except DownloadHistory.DoesNotExist:
                pass
        return None


class DownloadableSerializer(serializers.ModelSerializer):
    folder_contents = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    last_download_date = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Downloadable
        fields = ['id', 'updated_timestamp', 'folder_contents', 'file', 'last_download_date', 'name']

    def get_last_download_date(self, downloadable):
        user = self.context.get('user')
        if user and user.is_authenticated:
            try:
                return downloadable.download_history.filter(user=user).latest().timestamp
            except UserDownloadableHistory.DoesNotExist:
                pass
        return None

    @staticmethod
    def get_name(downloadable):
        if downloadable.folder:
            return downloadable.folder
        else:
            clean_name = downloadable.file.clean_name
            try:
                if clean_name.index('/') >= 0:
                    clean_name = clean_name.split("/")[-1]
            except ValueError:
                pass
            return clean_name

    def get_folder_contents(self, downloadable):
        user = self.context.get('user')
        contents = []
        for child in downloadable.get_children():  # TODO: Consider order by
            contents.append(DownloadableSerializer(child, context={'user': user}).data)
        return contents

    def get_file(self, downloadable):
        user = self.context.get('user')
        if downloadable.file is not None:
            return DIFileSerializer(downloadable.file, context={'user': user}).data
        return None


class DigitalItemSerializer(ItemSerializer):
    root_downloadable = DownloadableSerializer()
    available_for_download = serializers.SerializerMethodField()

    class Meta(ItemSerializer.Meta):
        model = DigitalItem
        fields = ItemSerializer.Meta.fields + (
            'download_overlay_banner', 'root_downloadable', 'available_for_download'
        )

    def get_download_overlay_banner(self, item):
        user = self.context.get('user')
        if user and user.is_authenticated:
            return item.download_overlay_banner(user)
        return None

    def get_available_for_download(self, item):
        user = self.context.get('user')
        if user and user.is_authenticated:
            return item.available_for_download()
        return False
