import pytest
from tri_declarative import Namespace
from tri_struct import Struct

from iommi import Field
from iommi.experimental.edit_table import (
    EditColumn,
    EditTable,
)
from tests.helpers import (
    req,
    verify_table_html,
)


@pytest.mark.django_db
def test_formset_table():
    edit_table = EditTable(
        sortable=False,
        columns=dict(
            editable_thing=EditColumn(
                edit=Namespace(call_target=Field),
            ),
            readonly_thing=EditColumn(),
        ),
        rows=[
            Struct(pk=1, editable_thing='foo', readonly_thing='bar'),
            Struct(pk=2, editable_thing='baz', readonly_thing='buzz'),
        ],
    )

    verify_table_html(
        table=edit_table.bind(request=req('get')),
        find=dict(method='post'),
        # language=html
        expected_html="""
            <form enctype="multipart/form-data" method="post">
                <div class="iommi-table-container">
                    <div class="iommi-table-plus-paginator">
                        <table class="table" data-endpoint="/endpoints/tbody" data-iommi-id="">
                            <thead>
                                <tr>
                                    <th class="first_column subheader"> Editable thing </th>
                                    <th class="first_column subheader"> Readonly thing </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr data-pk="1">
                                    <td>
                                         <input id="id_edit_form__editable_thing__1" name="edit_form/editable_thing/1" type="text" value="foo"/>
                                    </td>
                                    <td>
                                        bar
                                    </td>
                                </tr>
                                <tr data-pk="2">
                                    <td>
                                        <input id="id_edit_form__editable_thing__2" name="edit_form/editable_thing/2" type="text" value="baz"/>
                                    </td>
                                    <td>
                                        buzz
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="links">
                    <button accesskey="s" name="-submit"> Save </button>
                    <div style="display: none"> Csrf </div>
                </div>
            </form>
        """
    )


@pytest.mark.django_db
def test_formset_table_post():
    rows = [
        Struct(pk=1, editable_thing='foo', readonly_thing='bar', save=lambda: None, ),
        Struct(pk=2, editable_thing='baz', readonly_thing='buzz', save=lambda: None, ),
    ]
    edit_table = EditTable(
        columns=dict(
            # Should work but doesn't yet: editable_thing=EditColumn(edit=Field()),
            editable_thing=EditColumn(
                edit=Namespace(call_target=Field),
            ),
            readonly_thing=EditColumn(),
        ),
        rows=rows,
    )
    response = edit_table.bind(request=req('POST', **{
        'edit_form/editable_thing/1': 'fisk',
        'edit_form/editable_thing/2': 'fusk',
        '-submit': '',
    })).render_to_response()
    assert response.status_code == 302

    assert rows[0].editable_thing == 'fisk'
    assert rows[1].editable_thing == 'fusk'
