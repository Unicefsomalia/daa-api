import traceback
from os import path

import openpyxl
from background_task import background
from django.db.models import F
from openpyxl import Workbook
from openpyxl.utils.exceptions import InvalidFileException

from mylib.queryset2excel import (
    importExcelCsv,
    serializerToRow,
    get_header_column_name,
    serializerErrorToRow,
)
from region.models import District, Region, State, Village, SubCounty, County
from school.models import SchoolsStudentsImport, School, Stream, Student

from school.schools_students_imports.serializers import (
    StudentSchoolSerializer,
    SchoolImportSerializer,
)
from school.student.serializers import StudentSerializer
from somapi.settings import MEDIA_ROOT

# from iterable_orm import QuerySet


def get_state_id(valid_data, entity=""):
    state = valid_data.get("{}state".format(entity), None)
    if state == None:
        return None
    queryset = State.objects.filter(name__lower=state.lower())

    if queryset.exists():
        return queryset[0].id
    c = State.objects.create(name=state)
    return c.id


def get_region_id(valid_data, entity=""):
    region = valid_data.get("{}region".format(entity), None)
    if region == None:
        return None

    state_id = get_state_id(valid_data, entity)

    if state_id == None:
        return None

    queryset = Region.objects.filter(name__lower=region.lower(), state_id=state_id)

    if queryset.exists():
        return queryset[0].id
    c = Region.objects.create(name=region, state_id=state_id)
    return c.id


def get_district_id(valid_data, entity=""):
    district = valid_data.get("{}district".format(entity), None)
    if district == None:
        return None

    region_id = get_region_id(valid_data, entity)

    if region_id == None:
        return None

    queryset = District.objects.filter(name__lower=district.lower(), region_id=region_id)
    if queryset.exists():
        return queryset[0].id

    c = District.objects.create(name=district, region_id=region_id)
    return c.id


def get_village_id(valid_data, entity=""):
    village = valid_data.get("{}village".format(entity), None)
    if village == None:
        return None

    district_id = get_district_id(valid_data, entity)
    if district_id == None:
        return None

    queryset = Village.objects.filter(name__lower=village.lower(), district_id=district_id)
    if queryset.exists():
        return queryset[0].id

    sc = Village.objects.create(district_id=district_id, name=village)
    return sc.id


def get_school_from_nemis(valid_data):
    emis_code = valid_data.get("school_emis_code").upper()
    school = valid_data.get("school_name")
    # SchoolImportSerializer
    
    if School.objects.filter(emis_code=emis_code).exists():
        return School.objects.filter(emis_code=emis_code).first().id
    
    ## SubCounty
    village = get_village_id(valid_data, "school_")

    sch = School.objects.create(village_id=village, name=school, emis_code=emis_code)
    return sch.id


def get_stream_name(valid_data):
    stream = valid_data.get("stream").lower()
    school_emis_code = valid_data.get("school_emis_code")
    stream = stream.lower().replace("ecd", "0")
    extractedints = list(filter(lambda a: a.isdigit(), stream))
    # print(extractedints)
    if len(extractedints) < 1:
        return None
    stream = stream[stream.index(extractedints[0]) + 1 :]
    base_class = extractedints[0]
    res = (base_class, stream.replace(" ", ""))
    # print(res)
    return res


def get_stream_id(valid_data):
    stream = valid_data.get("stream")
    school = get_school_from_nemis(valid_data)
    
    try:
        st_name = get_stream_name(valid_data)
    except Exception as e:
        return None

    stream = st_name[1]
    base_class = st_name[0]

    streams = list(Stream.objects.filter(school_id=school, name=stream, base_class=base_class))
    try:
        if len(streams) < 1:
            sts = Stream.objects.create(name=stream, school_id=school, base_class=base_class)
            return sts.id
        else:
            return streams[0].id
    except Exception as e:
        print(e)
        return None


def get_stud_filters(
    first_name=None,
    middle_name=None,
    last_name=None,
    school_nemis_code=None,
    stream_name=None,
    base_class=None,
):
    queryFilters = {}
    if first_name:
        queryFilters["first_name__icontains"] = first_name

    if middle_name:
        queryFilters["middle_name__icontains"] = middle_name

    if last_name:
        queryFilters["last_name__icontains"] = last_name

    # if upi:
    #     queryFilters["upi"] = upi

    if school_nemis_code != None:
        queryFilters["stream__school__emis_code__icontains"] = school_nemis_code

    if stream_name != None:
        queryFilters["stream__name__icontains"] = stream_name

    if base_class != None:
        queryFilters["stream__base_class"] = base_class
    return queryFilters


def get_student_id(valid_data):
    # pass
    ## Ccounty and sub_Cunty

    ## TODO: Update has_special_needs
    school_village = get_village_id(valid_data, entity="learner_")
    village = get_village_id(valid_data, entity="learner_")
    if village == None and school_village:
        village = school_village

    guardian_village = get_village_id(valid_data, "guardian_")

    ## Confirm School Existst
    # school_id = get_school_from_nemis(valid_data)

    ## Confirm Stream Exists
    stream_id = get_stream_id(valid_data)
    # print(stream_id)
    # print(village, valid_data.get("learner_village"))
    # print(valid_data)
    if village == None:
        print(valid_data.get("learner_village"))

    if stream_id == None:
        return {"valid": False, "data": None, "error": "No Valid class provided"}

    ## Create Student
    # print(valid_data.get("date_of_birth"))
    # print(valid_data)
    stud_data = {
        "stream": stream_id,
        "gender": valid_data.get("gender"),
        "village": village,
        "guardian_village": guardian_village,
        "status": valid_data.get("status"),
        "first_name": valid_data.get("first_name"),
        "middle_name": valid_data.get("middle_name"),
        "last_name": valid_data.get("last_name"),
        "guardian_name": valid_data.get("guardian_name"),
        "guardian_phone": valid_data.get("guardian_phone"),
        "guardian_email": valid_data.get("guardian_email"),
        "date_enrolled": valid_data.get("date_enrolled").date(),
        "date_of_birth": valid_data.get("date_of_birth").date(),
        "distance_from_school": valid_data.get("distance_from_school"),
        "admission_no": valid_data.get("admission_number"),
    }
    st = StudentSerializer(data=stud_data)
    if not st.is_valid():
        print(st.errors)
        return {"valid": False, "data": None, "error": str(st.errors)}

    valid_stud = st.validated_data
    school_nemis_code = valid_data.get("school_emis_code").upper()
    # print(school_nemis_code)
    st_name = get_stream_name(valid_data)
    stream = st_name[1]
    base_class = st_name[0]

    queryFilters = get_stud_filters(
        first_name=valid_stud.get("first_name"),
        last_name=valid_stud.get("last_name"),
        middle_name=valid_stud.get("middle_name"),
        school_nemis_code=school_nemis_code,
        stream_name=stream,
        base_class=base_class,
    )

    # print(queryFilters)
    # print()
    queryset = Student.objects.filter(**queryFilters)

    if queryset.exists():
        return {"valid": True, "data": None}

    return {"valid": True, "data": valid_stud}


def append_import_count(import_id, rows_count):
    import_task = SchoolsStudentsImport.objects.get(id=import_id)
    import_task.append_count(rows_count)


def set_duplicates_count(import_id, count, total_count):
    import_task = SchoolsStudentsImport.objects.get(id=import_id)
    import_task.duplicates_count = count
    import_task.save()


# def set_errors()


@background(schedule=1)
def import_school_students(import_id):
    print("JOB IMpr\tImport:#{}".format(import_id))
    if not openpyxl.xml.lxml_available():
        SchoolsStudentsImport.objects.filter(id=import_id).update(step="F", errors="lxml not installed.")
        return
    ## Create an errors list Excel
    errors_wb = Workbook(write_only=True)
    errors_ws = errors_wb.create_sheet()
    error_rows = 0
    global students_to_create
    students_to_create = []
    # students_to_create

    try:
        import_task = SchoolsStudentsImport.objects.get(id=import_id)
        file_path = path.join(MEDIA_ROOT, import_task.import_file.name)
        # print(file_path)
        import_task.prepare_import()

        sheets_info_gen = importExcelCsv(filename=file_path, headers_only=True, include_rows_count=True)
        sheets = []
        for h in sheets_info_gen:
            sheets = h

        if len(sheets) < 1:
            import_task = SchoolsStudentsImport.objects.get(id=import_id)
            import_task.set_errors("No headers found")
            return

        sheet = sheets[0]
        rows_count = sheet["rows_count"]
        headers = sheet["headers"]

        # print(rows_count)

        import_task = SchoolsStudentsImport.objects.get(id=import_id)
        import_task.start(rows_count)
        ##Chek the first line

        ser = StudentSchoolSerializer()
        fields = ser.get_fields()
        required_fields = [f for f in fields if fields[f].required]

        missing_colums = []
        for required_field in required_fields:
            if required_field not in headers:
                missing_colums.append(required_field)

        if len(missing_colums) > 0:
            import_task = SchoolsStudentsImport.objects.get(id=import_id)
            import_task.set_errors("The following columns are required. {}".format(", ".join([get_header_column_name(header) for header in missing_colums])))
            return

        def get_row_number_title():
            return "row_number (Import #{})".format(import_id)

        ## Set up the errors file headers
        error_headers = [get_row_number_title()] + [f for f in fields] + ["error_description"]
        errors_ws.append([get_header_column_name(header) for header in error_headers])

        rowcount = 1
        global dulicates_count
        dulicates_count = 0
        global processed_row_count
        processed_row_count = 0
        new_students = 0

        def set_row_errors(row, row_number, error_description):
            row[get_row_number_title()] = row_number + 1
            row["error_description"] = str(error_description)
            try:
                # print(serializerErrorToRow(error_headers, row))
                errors_ws.append(serializerErrorToRow(error_headers, row))
            except Exception as e:
                print("Ws Appen", e)

        def bulk_create_students():
            global students_to_create
            res_count = len(Student.objects.bulk_create(students_to_create))
            print(res_count)
            students_to_create = []

            import_task = SchoolsStudentsImport.objects.get(id=import_id)
            import_task.new_students_created += res_count
            import_task.save()

        def create_new_student(new_student):
            global students_to_create
            global students_to_create_queryset
            Student.objects.create(**new_student)
            import_task = SchoolsStudentsImport.objects.get(id=import_id)
            import_task.new_students_created += 1
            import_task.save()
            return

        def set_duplicate_with_count():
            global dulicates_count
            global processed_row_count
            dulicates_count += 1
            set_row_errors(row, processed_row_count, "Duplicate")

        print("Processing rows")
        for row_info in importExcelCsv(filename=file_path):
            if processed_row_count >= rows_count:
                continue

            processed_row_count += 1

            try:
                if row_info["header_row"]:
                    processed_row_count -= 1
                    continue
                row = row_info["row"]
                # print(row)

                ser = StudentSchoolSerializer(data=row)
                if ser.is_valid():
                    # print(ser.validated_data)
                    valid_data = ser.validated_data
                    new_student_info = get_student_id(valid_data=valid_data)

                    if not new_student_info["valid"]:
                        error = new_student_info.get("error", "Unknow Error")
                        print(error)
                        error_rows += 1
                        set_row_errors(row, processed_row_count, error)

                    elif new_student_info["valid"]:
                        new_student = new_student_info["data"]
                        if new_student != None:
                            if import_task.should_import:
                                create_new_student(new_student)
                        else:
                            set_duplicate_with_count()
                else:
                    error_rows += 1
                    serialiserErrors = {}

                    for error in ser.errors:
                        serialiserErrors[error] = list(map(lambda erro: str(erro), ser.errors[error]))
                    errorsStringArray = list(
                        map(
                            lambda key: "{} - {}".format(
                                get_header_column_name(key),
                                ", ".join(serialiserErrors[key]),
                            ),
                            serialiserErrors,
                        )
                    )
                    #
                    errorsString = " \n".join(errorsStringArray)
                    print("\n", errorsString, "\n")
                    print(row, "\n")
                    set_row_errors(row, processed_row_count, errorsString)

                append_import_count(import_id, 1)
            except Exception as e:
                print(e)
                error_rows += 1
                set_row_errors(row, processed_row_count, e)
                pass

        # Create any remaining students.
        # create_new_student(None)

        ## If
        set_duplicates_count(import_id, dulicates_count, processed_row_count)
        import_task = SchoolsStudentsImport.objects.get(id=import_id)

        if error_rows > 0:
            file_path = path.join(MEDIA_ROOT, "imports", "Import-{}-Errors.xlsx".format(import_id))
            errors_wb.save(file_path)
            xp = SchoolsStudentsImport.objects.get(id=import_id)
            xp.finish(errors_file_path=file_path, error_rows_count=error_rows)
        else:
            import_task.finish()

        print(
            "Done",
            rows_count,
            "imported_rows_count=",
            import_task.imported_rows_count,
            "<-Add +->",
            "duplicates_count=",
            import_task.duplicates_count,
            "new_students_created=",
            import_task.new_students_created,
            "error_rows=",
            error_rows,
        )

    except InvalidFileException as ife:
        print("Error IFE")
        import_task = SchoolsStudentsImport.objects.get(id=import_id)
        import_task.set_errors(ife.args[0])
        # print(import_task.errors)
        print(ife)
        if error_rows > 0:
            file_path = path.join(MEDIA_ROOT, "imports", "Import-{}-Errors.xlsx".format(import_id))
            errors_wb.save(file_path)
            xp = SchoolsStudentsImport.objects.get(id=import_id)
            xp.finish(errors_file_path=file_path, error_rows_count=error_rows)
        else:
            import_task.finish()

    except Exception as e:
        import_task = SchoolsStudentsImport.objects.get(id=import_id)
        import_task.set_errors(str(e))
        print(type(e))
        print(e)

        print(traceback.format_exc())

        if error_rows > 0:
            file_path = path.join(MEDIA_ROOT, "imports", "Import-{}-Errors.xlsx".format(import_id))
            errors_wb.save(file_path)
            xp = SchoolsStudentsImport.objects.get(id=import_id)
            xp.finish(errors_file_path=file_path, error_rows_count=error_rows)
        else:
            import_task.finish()

    pass
