"""
Dialogs Module
"""

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

from app.utils.logger import LoggerMixin


class DialogManager(LoggerMixin):
    """Manager for application dialogs"""
    
    @staticmethod
    def show_error_dialog(title: str = "خطأ", 
                         message: str = "حدث خطأ غير متوقع",
                         callback=None) -> MDDialog:
        """
        Show error dialog
        
        Args:
            title: Dialog title
            message: Error message
            callback: Callback on dismiss
            
        Returns:
            Dialog instance
        """
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="موافق",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        
        if callback:
            dialog.bind(on_dismiss=callback)
        
        dialog.open()
        return dialog
    
    @staticmethod
    def show_success_dialog(title: str = "تم بنجاح",
                           message: str = "تمت العملية بنجاح",
                           callback=None) -> MDDialog:
        """
        Show success dialog
        
        Args:
            title: Dialog title
            message: Success message
            callback: Callback on dismiss
            
        Returns:
            Dialog instance
        """
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="موافق",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        
        if callback:
            dialog.bind(on_dismiss=callback)
        
        dialog.open()
        return dialog
    
    @staticmethod
    def show_confirm_dialog(title: str = "تأكيد",
                           message: str = "هل أنت متأكد؟",
                           on_confirm=None,
                           on_cancel=None) -> MDDialog:
        """
        Show confirmation dialog
        
        Args:
            title: Dialog title
            message: Confirmation message
            on_confirm: Confirm callback
            on_cancel: Cancel callback
            
        Returns:
            Dialog instance
        """
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: (
                        dialog.dismiss(),
                        on_cancel() if on_cancel else None
                    )
                ),
                MDRaisedButton(
                    text="موافق",
                    on_release=lambda x: (
                        dialog.dismiss(),
                        on_confirm() if on_confirm else None
                    )
                ),
            ]
        )
        
        dialog.open()
        return dialog
    
    @staticmethod
    def show_input_dialog(title: str = "إدخال",
                         hint_text: str = "",
                         on_submit=None,
                         on_cancel=None) -> MDDialog:
        """
        Show input dialog
        
        Args:
            title: Dialog title
            hint_text: Input hint
            on_submit: Submit callback with text
            on_cancel: Cancel callback
            
        Returns:
            Dialog instance
        """
        text_field = MDTextField(
            hint_text=hint_text,
            mode='rectangle',
            size_hint_y=None,
            height=dp(50)
        )
        
        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=text_field,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: (
                        dialog.dismiss(),
                        on_cancel() if on_cancel else None
                    )
                ),
                MDRaisedButton(
                    text="موافق",
                    on_release=lambda x: (
                        dialog.dismiss(),
                        on_submit(text_field.text) if on_submit else None
                    )
                ),
            ]
        )
        
        dialog.open()
        return dialog
    
    @staticmethod
    def show_progress_dialog(title: str = "جاري التحميل...",
                            message: str = "يرجى الانتظار") -> MDDialog:
        """
        Show progress dialog
        
        Args:
            title: Dialog title
            message: Progress message
            
        Returns:
            Dialog instance
        """
        from kivymd.uix.spinner import MDSpinner
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            adaptive_height=True
        )
        
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': 0.5}
        )
        content.add_widget(spinner)
        
        label = MDLabel(
            text=message,
            halign='center',
            theme_text_color='Secondary'
        )
        content.add_widget(label)
        
        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
            auto_dismiss=False
        )
        
        dialog.open()
        return dialog
    
    @staticmethod
    def show_quality_selection_dialog(qualities: list,
                                     current_quality: str,
                                     on_select=None) -> MDDialog:
        """
        Show quality selection dialog
        
        Args:
            qualities: List of quality strings
            current_quality: Currently selected quality
            on_select: Selection callback
            
        Returns:
            Dialog instance
        """
        from kivymd.uix.list import OneLineListItem
        
        items = []
        for quality in qualities:
            item = OneLineListItem(
                text=quality,
                on_release=lambda x, q=quality: (
                    dialog.dismiss(),
                    on_select(q) if on_select else None
                )
            )
            items.append(item)
        
        dialog = MDDialog(
            title="اختر الجودة",
            type="simple",
            items=items
        )
        
        dialog.open()
        return dialog
    
    @staticmethod
    def show_model_download_dialog(model_name: str,
                                  model_size: str,
                                  on_confirm=None,
                                  on_cancel=None) -> MDDialog:
        """
        Show model download confirmation dialog
        
        Args:
            model_name: Model name
            model_size: Model size
            on_confirm: Confirm callback
            on_cancel: Cancel callback
            
        Returns:
            Dialog instance
        """
        message = f"""
        سيتم تحميل النموذج: {model_name}
        الحجم: {model_size}
        
        قد يستغرق التحميل بعض الوقت حسب سرعة الاتصال.
        هل تريد المتابعة؟
        """
        
        return DialogManager.show_confirm_dialog(
            title="تحميل نموذج",
            message=message,
            on_confirm=on_confirm,
            on_cancel=on_cancel
        )