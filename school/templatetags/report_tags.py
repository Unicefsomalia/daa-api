from django import template
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.base import Token


register = template.Library()


class ReportStartEndTag(template.Node):
    def render(self, context):
        try:
            context = context.flatten()
        except Exception as e:
            print(e)
            context = {}
        rendered_template = render_to_string("tags/report_start_end.html", context=context)
        return rendered_template


@register.tag("report_start_end_date")
def report_start_end_date(parser, token):
    return ReportStartEndTag()


class ReportTableTag(template.Node):
    def __init__(self,field_name=None,args={},):
        super().__init__()
        self.field_name=field_name
        self.args=args

    def render(self, context):
        try:
            context = context.flatten()
        except Exception as e:
            print(e)
            context = {}
        # print("Field Name ins")
        # print(self.field_name)
        # print("Context ins")
        if self.field_name not in context:
            message=f"field name {self.field_name} not found "
            print(message)
        
        new_context=context.get(self.field_name,{})
        print( context["all_status_enrollment"])
        # print([key for key in context])
        new_context.update(self.args)
        
        # print(new_context)
    
        rendered_template = render_to_string("tags/report_table.html", context=new_context)
        return rendered_template

@register.tag("report_table_tag")
def report_table_tag(parser,token:Token):
    # print("Token in")
    # print(token.split_contents())
    field_name=token.split_contents()[1]
    args={
    }
    return ReportTableTag(field_name=field_name,args=args,)


@register.filter(name="title_case")
def title_case(value):
    return value.replace("_"," ").title()

@register.filter(name="json_value")
def json_value(json, key):
   
    try:
        return json.get(key,None)
    except Exception as e:
        # Todo: remove
        # raise e
        # print(f"Missing Key {key}, Set a default")
        return None

@register.filter(name='is_integer')
def is_integer(value):
    return isinstance(value, int) or isinstance(value, float)



class CustomTableTitleTag(template.Node):
    def __init__(self,title=None):
        super().__init__()
        self.title=title

    def render(self, context):
        try:
            context = context.flatten()
        except Exception as e:
            print(e)
            context = {}
        context.update({"table_title":self.title})
        # print("DAam context is ")
        # print(context)
        
        rendered_template = render_to_string("tags/custom_table_title.html", context=context)
        return rendered_template
    
@register.tag("custom_table_title")
def custom_table_title(parser,token:Token):
    # print(token)
    title=token.split_contents()[1:]
    # print(token.split_contents())
    # print(title)
    return CustomTableTitleTag(title=" ".join(title))



class CustomAttendanceOverviewCardsTag(template.Node):
    def __init__(self,title=None,field_name=None):
        super().__init__()
        self.title=title
        self.field_name=field_name

    def render(self, context):
        try:
            context = context.flatten()
        except Exception as e:
            context = {}
        context.update(
            {
            "table_title":self.title,
            "field_name":self.field_name
                        }
                       )
        rendered_template = render_to_string("tags/attendance_overview_cards.html", context=context)
        return rendered_template
    
@register.tag("attendance_overview_cards")
def custom_table_title(parser,token:Token):
    return CustomAttendanceOverviewCardsTag()



class CustomEnrollmentOverviewCardsTag(template.Node):
    def __init__(self,title=None,field_name=None):
        super().__init__()
        self.title=title
        self.field_name=field_name

    def render(self, context):
        try:
            context = context.flatten()
        except Exception as e:
            context = {}
        context.update(
            {
            "table_title":self.title,
            "field_name":self.field_name
                        }
                       )
        rendered_template = render_to_string("tags/enrollment_overview_cards.html", context=context)
        return rendered_template
    
@register.tag("enrollment_overview_cards")
def custom_table_title(parser,token:Token):
    return CustomEnrollmentOverviewCardsTag()




class CustomOverallStaticsCardsTag(template.Node):
    def __init__(self,title=None,field_name=None):
        super().__init__()
        self.title=title
        self.field_name=field_name

    def render(self, context):
        try:
            context = context.flatten()
        except Exception as e:
            context = {}
        context.update(
            {
            "table_title":self.title,
            "field_name":self.field_name
                        }
                       )
        rendered_template = render_to_string("tags/overall_statistics_tag.html", context=context)
        return rendered_template
    
@register.tag("overall_statistics_tag")
def custom_table_title(parser,token:Token):
    return CustomOverallStaticsCardsTag()