
from rest_framework import serializers
from school.models import OoscPartner
import school.signals as school_signals
from django.contrib.auth import get_user_model

MyUser=get_user_model()

class OoscPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model=OoscPartner
        fields=("__all__")
    
    def validate_email(self,value):
        pk=self.context.get("view").kwargs.get("pk",None)
        users_query=MyUser.objects.all()
        if pk!=None:
            users_query=users_query.exclude(partner=pk)
        
        if users_query.filter(username=value).exists():
            raise serializers.ValidationError("Email already used")
        
        return value
    
    def validate_schools(self,value):
        # print("GOt",value)
        return value
    
    def create(self, validated_data):
        res= super().create(validated_data)
        school_signals.partner_save.send(sender=OoscPartner,instance=res)
        return res
    
    def update(self, instance, validated_data):
        res= super().update(instance, validated_data)
        school_signals.partner_save.send(sender=OoscPartner,instance=res)
        return res
