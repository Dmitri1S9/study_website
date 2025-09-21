from rest_framework import routers
from .views import CharacterViewSet, TitleViewSet, ParsingMaterialsViewSet

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(r'characters', CharacterViewSet)
router.register(r'parsing_materials', ParsingMaterialsViewSet)

urlpatterns = router.urls