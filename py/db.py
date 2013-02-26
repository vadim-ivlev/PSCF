import json
import os
#import types
from google.appengine.api import rdbms
import logging
import time
import StringIO
import csv


_INSTANCE_NAME = 'sovdefdatabase:sovdef'
_DB='pscf1'
_USER_NAME = 'root'
_PASSWORD = ''


# def getConnectionOnly():
#     if os.environ['SERVER_SOFTWARE'].find('Development') >= 0:
#         logging.info("getConnectionOnly: connected to local MySQL")
#         return rdbms.connect(instance=_INSTANCE_NAME, database=_DB)
# #        return rdbms.connect(instance=_INSTANCE_NAME, database=_DB, user=_USER_NAME, password=_PASSWORD)
#     else:
#         logging.info("getConnectionOnly: connected to Cloud SQL")
#         return rdbms.connect(instance=_INSTANCE_NAME, database=_DB)
#
# def showCharset(cursor):
#     jsonString=executeSelect(cursor," SHOW VARIABLES LIKE 'character_set%' ")
#     logging.info(jsonString)




def getConnection():
    connection = None
    cursor = None

    if os.environ['SERVER_SOFTWARE'].find('Development') >= 0:
        connection = rdbms.connect(instance='', database=_DB, user=_USER_NAME, password=_PASSWORD, host='localhost')
        # connection = rdbms.connect(instance=_INSTANCE_NAME, database=_DB)
        logging.info("getConnection: connected to local MySQL")
    else:
        connection = rdbms.connect(instance=_INSTANCE_NAME, database=_DB)
        logging.info("getConnection: connected to Cloud SQL")

    cursor =connection.cursor()
    # otherwise character_set_client, character_set_connection, character_set_results == utf8mb4, which is superset of utf8
#    cursor.execute('SET NAMES utf8 COLLATE utf8_general_ci;')
#    showCharset(cursor)
    return (connection,cursor)


def executeSelect(cursor,selectQuery ):
    """
    Executes selectQuery and  returns database recordset
    serialized into JSON string.
    """
    t0=time.time()
    cursor.execute(selectQuery)
    columns_description = cursor.description
    rows=cursor.fetchall()

    t1=time.time()
    jsonString=getJsonString(rows,columns_description )

    t2=time.time()
    logging.info("executeSelect: Query+Fetch:%s sec. Serializing:%s sec." % (t1-t0,t2-t1))

    return jsonString


def adjustValue(value, isRunningOnCloud):
    if isRunningOnCloud:
#        return value
        return "%s" % value
    else:
        return unicode(str(value), errors="ignore")
#        return "%s" % value


def getJsonString(rows, columns_description):
    isRunningOnCloud= (os.environ['SERVER_SOFTWARE'].find('Development') < 0)

    result = []
    for row in rows:
        tmp = {}
        for (col_index,value) in enumerate(row):
            tmp[columns_description[col_index][0]] = adjustValue(value,isRunningOnCloud)
        result.append(tmp)
    s=json.dumps(result)
    return s


def jsonToCSV(jsonString):
    list=json.loads(jsonString)
    if len(list)==0 : return ''

    tmp = StringIO.StringIO()
    writer = csv.writer(tmp)

    fieldNames=[]
    for fName in list[0]:
        fieldNames.append(fName)
    writer.writerow(fieldNames)

    for i in range(len(list)):
        values=[]
        dict=list[i]
        for fname in dict:
            v=dict[fname]
            s='%s' % v
            if s.find(u'\xa0')!=-1:
                logging.info("Found strange symbol xa0 in field: %s" % fname)
                s=s.replace(u'\xa0',' ')
            values.append(s)

#            if fname=='source':
#                s=u'%s' % v
#                if s.find(u'\xa0')!=-1:
#                    logging.info("Found strange symbol")
#                    s=s.replace(u'\xa0',' ')
#                values.append(s)
#            else:
#                values.append(v)
        writer.writerow(values)

    contents = tmp.getvalue()

    tmp.close()
    return contents


def jsonToHTML(jsonString):
    list=json.loads(jsonString)
    if len(list)==0 : return ''

    html = '''
    <html>
    <head>
    <title>Fiscal Data</title>
    </head>
    <body>
    <table>'''

    html+='<th>'
    for fName in list[0]: html+='<td>%s</td>' % fName
    html+='</th>'

    for i in range(len(list)):
        html+='<tr>'
        dict=list[i]
        for fname in dict: html+='<td>%s</td>' % dict[fname]
        html+='</tr>'

    html += '''
    </table>
    </body>
    </html>'''

    return html






def fromJsonString(jsonStr):
    return json.loads(jsonStr)








def buildUpdateQuery(tableName, keyFieldName,field_name, changed_by,  jsonString):
    list=fromJsonString(jsonString)
    dict=list[0] #jsonWriter allowSingle=false

    # if batch update, we take the last elem
#    if isinstance(dict, types.ListType):
#        dict=dict[0]


    s='UPDATE %s SET ' % tableName

    keyValue=dict[keyFieldName]

    #check if the key is defined
    if keyValue=='':
        return ''

    # set the changer name
    if field_name is not None:
        dict[field_name]=changed_by

    #remove the key field from the field to update
    del dict[keyFieldName]

    lastN=len(dict)-1
    for i, (k, v) in enumerate(dict.iteritems()):
        s+='%s=\'%s\' ' % (k, v)
        if i < lastN:
            s+=', '
        s+=' '

    s+="WHERE %s=%s" % (keyFieldName, keyValue)
    return (keyValue, s)


def isModerator(cursor, user_name):
    """
    Checks is the user has "moderator" privileges
    """
    query="SELECT * FROM users_roles WHERE ( name='any_user' and role='moderator' ) or ( name='%s' and role='moderator' ) LIMIT 1" % user_name
    cursor.execute(query)
    row=cursor.fetchone()
    if row is None:
        return False
    else:
        return True


def isSpammer(cursor, user_name):
    """
    Checks if the user is a spammer
    """
    query="SELECT * FROM users_roles WHERE ( name='any_user' and role='spammer' ) or ( name='%s' and role='spammer' ) LIMIT 1" % user_name
    cursor.execute(query)
    row=cursor.fetchone()
    if row is None:
        return False
    else:
        return True



