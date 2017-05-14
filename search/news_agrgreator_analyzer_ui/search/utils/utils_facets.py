from __future__ import print_function
from utils_sphinx_connector import Connector


class FacetConnectorCreator(object):

    def __init__(self):
        self.sphinx_connector = Connector(host="127.0.0.1", port=9306, options={})

    def execute_facet(self, final_query):
        obj_sphinx_connector = FacetConnectorCreator()
        sphinx_con = obj_sphinx_connector.sphinx_connector.get_connection()
        sphinx_cursor = sphinx_con.cursor()

        result_dict = {}
        sphinx_cursor.execute(final_query)
        result_dict['facet_id'] = sphinx_cursor.fetchall()
        sphinx_cursor.nextset()
        result_dict['main'] = sphinx_cursor.fetchall()

        obj_sphinx_connector.sphinx_connector.put_connection(sphinx_con)
        return result_dict['main']
