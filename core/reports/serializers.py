
from rest_framework import serializers
from django.utils import timezone
import stats.models as stats_models
from core.reports.get_data import get_any_stats
import math

def calc_total(x):
    x["total_attendances_taken"]=x["total_attendances_taken"]*19721
    return x


class CustomSeriliazerField(serializers.Field):
    def __init__(self,items_name=None,list_size=None,activity=None,all_time=False,convert_to_dict=False,preChartDataFunctions=[], grouping=None,grouping_plural=None,order_by=None,display_name_field=None,display_value_field=None, endpoint=None,filters=None,headers=None, **kwargs):
        kwargs["source"]="*"
        super().__init__(**kwargs)
        self.grouping = grouping
        self.endpoint = endpoint
        self.filters=filters
        self.order_by=order_by
        self.activity=activity
        self.headers=headers
        self.list_size=list_size
        self.all_time=all_time
        self.items_name=items_name
        self.preChartDataFunctions=preChartDataFunctions
        self.grouping_plural=grouping_plural,
        self.display_name_field=display_name_field
        self.display_value_field=display_value_field
        self.convert_to_dict=convert_to_dict
        
    def get_query_parms(self, obj,order="DESC",page_size=None):
        query_params = {}

        if obj.start_date:
            if not self.all_time:
                query_params["start_date"] = obj.start_date.strftime("%Y-%m-%d")

        if obj.end_date:
            if not self.all_time:
                query_params["end_date"] = obj.end_date.strftime("%Y-%m-%d")
        
        if self.order_by:
            query_params["order_by"]=self.order_by
        
        if order:
            query_params["order"]=order
            
        query_params["cache_timeout"]=-1
        query_params["cache_timeout"]=False

        if page_size:
            query_params["page_size"]=page_size
        else:
            query_params["page_size"] = obj.list_size if obj.list_size else 100
        return query_params
    
    def to_representation(self, value):
        try:
            list_size= value.list_size if self.list_size==None else self.list_size
            top_page_size= math.floor(list_size/2*1.0)
            least_page_size=list_size-top_page_size
            
            response = get_any_stats(model=self.endpoint, grouping=self.grouping, user=value.user, query_params=self.get_query_parms(value,order="DESC",page_size=top_page_size),)
            # print(response)
            default_name=self.endpoint if self.items_name==None else self.items_name
            default_response={
                'headers':self.headers,
                'name':default_name,
                'grouping':self.grouping,
                'activity':default_name if self.activity==None else self.activity,
                'grouping_plural': self.grouping ,#if self.grouping_plural==None else self.grouping_plural,
                'display_name_field':self.display_name_field,
                'display_value_field':self.display_value_field,
            }
            # For non paginated and single results
            if "count" not in response:
                if type(response)== dict:
                    print("nine")
                    return {
                        ** response,#list(map(lambda x:calc_total(x),items)),
                        **default_response 
                    }
                else:
                    print("hello")
                    return {
                       'list': items,#list(map(lambda x:calc_total(x),items)),
                        **default_response 
                    }
            
            
            count = response["count"]
            received_items = response["results"]
            items=[]
            #  Append new keys 
            try:
                if len(self.preChartDataFunctions)>0:
                    for raw_item in received_items:
                        new_item={**raw_item}
                        for func in self.preChartDataFunctions:
                            if "func" in func :
                                new_item[func.get("name")]=func.get("func")(raw_item)
                        items.append(new_item)
                else:
                    items=received_items
            except Exception as e:
                # TODO: remove
                # raise e
                items=received_items
        
            
            dict_results={}
            if self.convert_to_dict:
                for item in items:
                    try:
                        key=item.get(self.display_name_field).lower().replace("-","_").replace(" ","_")
                        item_value=item.get(self.display_value_field)
                        dict_results[key]=item
                    except Exception as e:
                        print(e)
                print(dict_results)
                
                
            top=None
            if(len(items)>0):
                top=items[0]
            
            least=None
            least_response = get_any_stats(model=self.endpoint, grouping=self.grouping, user=value.user, query_params=self.get_query_parms(value,order="ASC",page_size=least_page_size))
            received_least_items = least_response["results"]
            
            if(len(received_least_items)>0):
                least=received_least_items[0]
                
            
            top_values=list(map(lambda x:x["value"],items))
            least_items= list(filter(lambda x:x["value"] not in top_values,received_least_items))
            
    
            
            final_least_items=[]
            
            try:
                if len(self.preChartDataFunctions)>0:
                    for least_raw_item in least_items:
                        new_least_item={**least_raw_item}
                        for func in self.preChartDataFunctions:
                            if "func" in func :
                                new_least_item[func.get("name")]=func.get("func")(least_raw_item)
                        final_least_items.append(new_least_item)
                else:
                    final_least_items=  least_items
                    
            except Exception as e:
                # TODO: remove
                # raise e
                final_least_items=least_items
            
             
            return {
                'count':count,
                'list': items,#list(map(lambda x:calc_total(x),items)),
                'least_items':final_least_items[::-1],
                'top_list_size':top_page_size,
                'least_list_size':least_page_size,
                'top':top,
                 'least':least,
                # 'list_size':value.list_size,
                'dict_results':dict_results,
                **default_response
            }
        except Exception as e:
            # TODO: remove
            # raise e
            return None
        

# county_enrolment = serializers.SerializerMethodField(method_name="get_counties_enrollment")
# total_county_enrolments = serializers.SerializerMethodField(method_name="get_counties_enrollment")
# top_county_enrolment = serializers.ReadOnlyField(default=None)
# least_county_enrolment = serializers.ReadOnlyField(default=None)

# [sub], grouping of sub and filter of county
# top_county_enrolment_school = serializers.ReadOnlyField(default=None)
# total_county_enrolment_schools = serializers.ReadOnlyField(default=None)

"""
grouping - state
endpoint - students

subs=[
    {   "name":"School",
        "grouping":"school",
        "filter_name":"school_state"
    },
    {
        "name":"Region",
        "grouping":"region",
        "filter_name":"school_state"
    }
]

"""    


def calculate_gender_attendance(row):
    if "present_count" not in row:
        return None
    total_attendances = row["total_attendances_taken"]
    value= 0 if total_attendances < 1 else row["present_count"] * 100.0 / total_attendances
    return value

def calculate_male_attendance(row):
    if "present_males" not in row:
        return None
    total_males = row["present_males"] + row["absent_males"]
    value= 0 if total_males < 1 else row["present_males"] * 100.0 / total_males
    return "{:.0f}%".format(value) 
    
def calculate_female_attendance(row):
    if "present_males" not in row:
        return None
    total_females = row["present_females"] + row["absent_females"]
    value= 0 if total_females < 1 else row["present_females"] * 100.0 / total_females
    return "{:.0f}%".format(value) 
    
def calculate_combined_attendance(row):
    if "present_males" not in row:
        return None
    total_males = row["present_males"] + row["absent_males"]
    total_females = row["present_females"] + row["absent_females"]
    total=total_males+total_females
    total_present=row["present_males"]+row["present_females"]
    value= 0 if total < 1 else total_present * 100.0 / total
    return value
    
    
enrollment_default_fields=["females","males","total_students"]
attendance_default_fields=["female_present_percentage","male_present_percentage","total_days"]
above_school_level_responses=["schools_that_marked"]
default_enrollment_kwargs={
    "endpoint":"students",
    "display_value_field":"total_students",
    "order_by":"total_students",
    "items_name":"new learners",
    "activity":"enrollment",
}
default_attendance_kwargs={
    "endpoint":"attendances",
    "display_value_field":"total_days",
    "order_by":"total_days",
    "items_name":"days",
    "activity":"attendance marked",
    "preChartDataFunctions":[
        {
            "name":"male_present_percentage",
            "func":calculate_male_attendance
        },
         {
            "name":"female_present_percentage",
            "func":calculate_female_attendance
        },
         {
            "name":"present_percentage",
            "func":calculate_female_attendance
        },
    ]
}


class OverCustomReportSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(default="Sample Title")
    subtitle = serializers.ReadOnlyField(default="Sample Subtlte")
    generated_on = serializers.ReadOnlyField(default=timezone.now())
    start_date = serializers.ReadOnlyField(required=False)
    end_date = serializers.ReadOnlyField(
        required=False,
    )
    
    overall_stats=CustomSeriliazerField(
                                           endpoint="all",
                                           grouping="",
                                           )
    
    all_status_enrollment=CustomSeriliazerField(
                                           **default_enrollment_kwargs,
                                           grouping="status",
                                           convert_to_dict=True,
                                            all_time=True,
                                            list_size=10,
                                            display_name_field="status_name",
                                            headers=["status_name",*enrollment_default_fields]
                                           ) 
    
    status_enrollment=CustomSeriliazerField(
                                           **default_enrollment_kwargs,
                                           grouping="status",
                                           convert_to_dict=True,
                                           list_size=10,
                                            display_name_field="status_name",
                                            headers=["status_name",*enrollment_default_fields]
                                           )
    
    state_enrollment=CustomSeriliazerField(
                                            **default_enrollment_kwargs,
                                           grouping="state",
                                            display_name_field="state_name",
                                            
                                            headers=["state_name",*enrollment_default_fields]
                                           )
    
    
    region_enrollment=CustomSeriliazerField(
                                           grouping="region",
                                           **default_enrollment_kwargs,
                                           display_name_field="region_name",
                                            headers=["state_name","region_name",*enrollment_default_fields]
                                           )
    
    partner_enrollment=CustomSeriliazerField(
                                             grouping="partner",
                                             **default_enrollment_kwargs,
                                             display_name_field="name",
                                             headers=["name",*enrollment_default_fields]
                                             )
    
    school_enrollment=CustomSeriliazerField(
                                             grouping="school",
                                             **default_enrollment_kwargs,
                                            display_name_field="school_name",
                                           headers=["school_name","state_name","region_name","district_name","village_name",*enrollment_default_fields]
                                             )
    
    district_enrollment=CustomSeriliazerField(
                                             grouping="district",
                                             **default_enrollment_kwargs,
                                            display_name_field="district_name",
                                           headers=["state_name","region_name","district_name",*enrollment_default_fields]
                                             )
    class_enrollment=CustomSeriliazerField(grouping="class",
                                           **default_enrollment_kwargs,
                                           display_name_field="class_name",
                                           headers=["class_name" ,*enrollment_default_fields])
    
    village_enrollment=CustomSeriliazerField(grouping="village",
                                           **default_enrollment_kwargs,
                                           display_name_field="village_name",
                                           headers=["village_name","state_name","region_name","district_name" ,*enrollment_default_fields]
                                           )
    gender_enrollment=CustomSeriliazerField(grouping="gender",
                                            convert_to_dict=True,
                                           **default_enrollment_kwargs,
                                           display_name_field="gender_name",
                                           list_size=10,
                                           headers=["gender_name" ,*enrollment_default_fields]
                                           )
    ## Attendance 
    status_attendance=CustomSeriliazerField(grouping="student-status",
                                           **default_attendance_kwargs,
                                           convert_to_dict=True,
                                           list_size=10,
                                           display_name_field="status_name",
                                           headers=["status_name",*above_school_level_responses ,*attendance_default_fields]
                                           )
    gender_attendance=CustomSeriliazerField(grouping="gender",
                                           **{
                                               **default_attendance_kwargs,
                                              "preChartDataFunctions":[
                                               {
                                                   "name":"present_percentage",
                                                   "func":calculate_gender_attendance
                                               }
                                                ],
                                            },
                                           list_size=10,
                                           convert_to_dict=True,
                                           display_name_field="gender_name",
                                           
                                           headers=["gender_name",*above_school_level_responses ,*attendance_default_fields]
                                           )
    class_attendance=CustomSeriliazerField(grouping="class",
                                           **default_attendance_kwargs,
                                           display_name_field="class_name",
                                           headers=["class_name",*above_school_level_responses ,*attendance_default_fields]
                                           )
    
    state_attendance=CustomSeriliazerField(
                                           grouping="state",
                                            **default_attendance_kwargs,
                                            display_name_field="state_name",
                                            headers=["state_name",*above_school_level_responses,*attendance_default_fields]
                                           )
    
    region_attendance=CustomSeriliazerField(
                                           grouping="region",
                                           **default_attendance_kwargs,
                                           display_name_field="region_name",
                                            headers=["state_name","region_name",*above_school_level_responses,*attendance_default_fields]
                                           )
    
    partner_attendance=CustomSeriliazerField(
                                             grouping="partner",
                                           **default_attendance_kwargs,
                                             display_name_field="name",
                                             headers=["name",*above_school_level_responses,*attendance_default_fields]
                                             )
    
    school_attendance=CustomSeriliazerField(
                                             grouping="school",
                                           **default_attendance_kwargs,
                                            display_name_field="school_name",
                                           headers=["school_name","state_name","region_name","district_name","village_name",*attendance_default_fields]
                                             )
    
    district_attendance=CustomSeriliazerField(
                                             grouping="district",
                                           **default_attendance_kwargs,
                                            display_name_field="district_name",
                                           headers=["state_name","region_name","district_name",*above_school_level_responses,*attendance_default_fields]
                                             )
    
    
    village_attendance=CustomSeriliazerField(grouping="village",
                                           **default_attendance_kwargs,
                                           display_name_field="village_name",
                                           headers=["village_name","state_name","region_name","district_name",*above_school_level_responses ,*attendance_default_fields]
                                           )
    
    attendance_fields=serializers.SerializerMethodField(method_name="get_attendance_keys",read_only=True)
    enrollment_fields=serializers.SerializerMethodField(method_name="get_enrollment_keys",read_only=True)

    
    class Meta:
        model=stats_models.Export
        fields=("__all__")
    
    def get_attendance_keys(self,obj):
        fields=[d for d in self.fields]
        return list(filter(lambda x:"attendance" in x,fields))
    
    def get_enrollment_keys(self,obj):
        fields=[d for d in self.fields]
        return list(filter(lambda x:"enrollment" in x,fields))
        
        
        