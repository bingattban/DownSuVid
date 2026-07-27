"""
Custom Widgets Module
"""

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp
from kivy.animation import Animation


class DownloadCard(MDCard):
    """Custom card widget for download items"""
    
    title = StringProperty("")
    status = StringProperty("")
    progress = NumericProperty(0)
    speed = StringProperty("")
    eta = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.elevation = 5
        self.radius = [15]
        self.size_hint_y = None
        self.height = dp(140)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build widget UI"""
        # Title
        self.title_label = MDLabel(
            text=self.title,
            font_style='Subtitle1',
            bold=True,
            theme_text_color='Primary'
        )
        self.add_widget(self.title_label)
        
        # Progress bar
        self.progress_bar = MDProgressBar(
            value=self.progress,
            max=100,
            type='determinate'
        )
        self.add_widget(self.progress_bar)
        
        # Info row
        info_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            adaptive_height=True
        )
        
        self.status_label = MDLabel(
            text=self.status,
            font_style='Caption',
            theme_text_color='Secondary',
            size_hint_x=0.4
        )
        info_box.add_widget(self.status_label)
        
        self.speed_label = MDLabel(
            text=self.speed,
            font_style='Caption',
            theme_text_color='Secondary',
            size_hint_x=0.3,
            halign='center'
        )
        info_box.add_widget(self.speed_label)
        
        self.eta_label = MDLabel(
            text=self.eta,
            font_style='Caption',
            theme_text_color='Secondary',
            size_hint_x=0.3,
            halign='right'
        )
        info_box.add_widget(self.eta_label)
        
        self.add_widget(info_box)
    
    def on_title(self, instance, value):
        """Update title"""
        self.title_label.text = value
    
    def on_progress(self, instance, value):
        """Update progress"""
        self.progress_bar.value = value
    
    def on_status(self, instance, value):
        """Update status"""
        self.status_label.text = value
    
    def on_speed(self, instance, value):
        """Update speed"""
        self.speed_label.text = value
    
    def on_eta(self, instance, value):
        """Update ETA"""
        self.eta_label.text = value
    
    def fade_out(self, callback=None):
        """Fade out animation"""
        anim = Animation(opacity=0, duration=0.5)
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        anim.start(self)


class ModelPackageCard(MDCard):
    """Custom card for model/package items"""
    
    name = StringProperty("")
    description = StringProperty("")
    size = StringProperty("")
    installed = BooleanProperty(False)
    downloading = BooleanProperty(False)
    progress = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(8)
        self.elevation = 5
        self.radius = [15]
        self.size_hint_y = None
        self.height = dp(130)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build widget UI"""
        # Name
        name_label = MDLabel(
            text=self.name,
            font_style='Subtitle1',
            bold=True,
            theme_text_color='Primary'
        )
        self.add_widget(name_label)
        self._name_label = name_label
        
        # Description
        desc_label = MDLabel(
            text=self.description,
            font_style='Caption',
            theme_text_color='Secondary'
        )
        self.add_widget(desc_label)
        self._desc_label = desc_label
        
        # Size
        size_label = MDLabel(
            text=f"الحجم: {self.size}",
            font_style='Caption',
            theme_text_color='Secondary'
        )
        self.add_widget(size_label)
        self._size_label = size_label
        
        # Progress bar (hidden by default)
        self.progress_bar = MDProgressBar(
            value=0,
            max=100,
            type='determinate',
            opacity=0
        )
        self.add_widget(self.progress_bar)
        
        # Action button
        button_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            adaptive_height=True
        )
        
        self.action_button = MDFlatButton(
            text='تحميل' if not self.installed else 'حذف',
            icon='download' if not self.installed else 'delete',
            size_hint_x=0.5
        )
        button_box.add_widget(self.action_button)
        
        self.add_widget(button_box)
    
    def on_installed(self, instance, value):
        """Update installed state"""
        if value:
            self.action_button.text = 'حذف'
            self.action_button.icon = 'delete'
        else:
            self.action_button.text = 'تحميل'
            self.action_button.icon = 'download'
    
    def on_downloading(self, instance, value):
        """Update downloading state"""
        if value:
            self.progress_bar.opacity = 1
            self.action_button.text = 'إلغاء'
            self.action_button.icon = 'close'
        else:
            self.progress_bar.opacity = 0
            self.on_installed(self, self.installed)
    
    def on_progress(self, instance, value):
        """Update progress"""
        self.progress_bar.value = value
    
    def on_name(self, instance, value):
        """Update name"""
        self._name_label.text = value
    
    def on_description(self, instance, value):
        """Update description"""
        self._desc_label.text = value
    
    def on_size(self, instance, value):
        """Update size"""
        self._size_label.text = f"الحجم: {value}"


class URLTextField(MDBoxLayout):
    """Custom URL text field with paste and clear buttons"""
    
    text = StringProperty("")
    hint_text = StringProperty("أدخل الرابط هنا...")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.adaptive_height = True
        
        from kivymd.uix.textfield import MDTextField
        
        self.text_field = MDTextField(
            hint_text=self.hint_text,
            mode='rectangle',
            size_hint_x=0.8,
            multiline=False
        )
        self.add_widget(self.text_field)
        
        self.paste_button = MDIconButton(
            icon='content-paste',
            size_hint_x=0.1
        )
        self.add_widget(self.paste_button)
        
        self.clear_button = MDIconButton(
            icon='close-circle',
            size_hint_x=0.1
        )
        self.add_widget(self.clear_button)


class StorageInfoWidget(MDCard):
    """Widget for displaying storage information"""
    
    used_space = StringProperty("0 MB")
    free_space = StringProperty("0 MB")
    total_space = StringProperty("0 MB")
    usage_percentage = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.elevation = 5
        self.radius = [15]
        self.size_hint_y = None
        self.height = dp(160)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build widget UI"""
        # Title
        title_label = MDLabel(
            text='مساحة التخزين',
            font_style='H6',
            bold=True,
            theme_text_color='Primary'
        )
        self.add_widget(title_label)
        
        # Progress bar
        self.storage_bar = MDProgressBar(
            value=self.usage_percentage,
            max=100,
            type='determinate'
        )
        self.add_widget(self.storage_bar)
        
        # Info labels
        info_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(5),
            adaptive_height=True
        )
        
        self.used_label = MDLabel(
            text=f"المستخدم: {self.used_space}",
            font_style='Caption',
            theme_text_color='Secondary'
        )
        info_box.add_widget(self.used_label)
        
        self.free_label = MDLabel(
            text=f"المتاح: {self.free_space}",
            font_style='Caption',
            theme_text_color='Secondary'
        )
        info_box.add_widget(self.free_label)
        
        self.total_label = MDLabel(
            text=f"الإجمالي: {self.total_space}",
            font_style='Caption',
            theme_text_color='Secondary'
        )
        info_box.add_widget(self.total_label)
        
        self.add_widget(info_box)