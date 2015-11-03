from django.contrib import admin
from article.models import Article 
from article.forms import ArticleAdminForm
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

	
class ArticleAdmin(admin.ModelAdmin):
	list_display 	= ('title', 'created')
	search_fields 	= ('title', 'content')
	list_filter 	= ('created',)
	form 			= ArticleAdminForm
	

admin.site.register(Article, ArticleAdmin)



