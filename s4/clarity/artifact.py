# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import WrappedXml, FieldsMixin, ClarityElement
from ._internal.props import subnode_property, subnode_element_list, attribute_property, subnode_link
from s4.clarity.file import File
from s4.clarity.configuration.stage import Stage
from s4.clarity.process import Process

QC_PASSED = "PASSED"
QC_FAILED = "FAILED"
QC_UNKNOWN = "UNKNOWN"


STAGE_STATUS_QUEUED = "QUEUED"
STAGE_STATUS_REMOVED = "REMOVED"
STAGE_STATUS_IN_PROGRESS = "IN_PROGRESS"


class WorkflowStageHistory(WrappedXml):

    uri = attribute_property("uri")
    status = attribute_property("status")
    name = attribute_property("name")
    stage = subnode_link(Stage, ".")


class ReagentLabel(WrappedXml):
    name = attribute_property("name", readonly=True)


class Artifact(FieldsMixin, ClarityElement):
    """
    Reference: https://www.genologics.com/files/permanent/API/latest/data_art.html#artifact
    """
    UNIVERSAL_TAG = "{http://genologics.com/ri/artifact}artifact"

    type = subnode_property("type")
    output_type = subnode_property("output-type")
    location_value = subnode_property("location/value")
    workflow_stages = subnode_element_list(WorkflowStageHistory, "workflow-stages", "workflow-stage", readonly=True)
    reagent_labels = subnode_element_list(ReagentLabel, ".", "reagent-label", readonly=True)
    parent_process = subnode_link(Process, 'parent-process')

    def __init__(self, lims,  uri=None, xml_root=None, name=None, limsid=None):
        super(Artifact, self).__init__(lims, uri, xml_root, name, limsid)

    @property
    def parent_step(self):
        """:type: Step"""
        return self.lims.steps.from_link_node(self.xml_find("./parent-process"))

    @property
    def sample(self):
        """:type: Sample"""
        return self.lims.samples.from_link_node(self.xml_find("./sample"))

    @property
    def samples(self):
        """:type: list[Sample]"""
        return self.lims.samples.from_link_nodes(self.xml_findall("./sample"))

    @property
    def file(self):
        """:type: File"""
        f = self.lims.files.from_link_node(self.xml_find('./{http://genologics.com/ri/file}file'))
        if f is None:
            f = File.new_empty(self)
            f.name = self.name
        return f

    @property
    def is_control(self):
        """:type: bool"""
        return self.xml_find('./control-type') is not None

    @property
    def control_type(self):
        """:type: ControlType"""
        return self.lims.control_types.from_link_node(self.xml_find("./control-type"))

    @property
    def queued_stages(self):
        """:type: set[Stage]"""
        queued_stages = set()
        for stage_history in self.workflow_stages:
            if stage_history.status == STAGE_STATUS_QUEUED:
                queued_stages.add(stage_history.stage)
            elif stage_history.status == STAGE_STATUS_REMOVED or stage_history.status == STAGE_STATUS_IN_PROGRESS:
                # It is possible a QUEUED stage history was left in the list. Remove if present
                queued_stages.discard(stage_history.stage)

        return queued_stages

    @property
    def qc(self):
        """
        Whether QC is marked as PASSED or FAILED on the artifact

        ============= ==========
        Clarity Value Bool Value
        ============= ==========
        PASSED        True
        FAILED        False
        UNKNOWN       None
        ============= ==========

        :type: bool
        """
        qctext = self.get_node_text('qc-flag')
        if qctext == QC_PASSED:
            return True
        elif qctext == QC_FAILED:
            return False
        else:
            return None

    @qc.setter
    def qc(self, value):
        """
        :type value: bool
        """
        self.set_qc_flag(value)

    def qc_passed(self):
        """:rtype: bool"""
        return self.get_node_text('qc-flag') == QC_PASSED

    def qc_failed(self):
        """:rtype: bool"""
        return self.get_node_text('qc-flag') == QC_FAILED

    def set_qc_flag(self, value):
        """
        The `qc` property should be used in favor of this method.

        :type value: bool
        :param value: `True` if PASSED, `False` if FAILED, `None` to unset.
        """
        if value is None:
            qc = QC_UNKNOWN
        elif value:
            qc = QC_PASSED
        else:
            qc = QC_FAILED
        self.set_subnode_text('qc-flag', qc)

    # TODO: move this to another file/class, or something.
    def open_file(self, mode, only_write_locally=False, name=None):
        """
        :type mode: str
        :param mode: 'r', 'r+', 'w', 'a', 'rb', 'r+b', 'wb', 'ab'.
            NOTE: 'r+' sets initial file position to the beginning, 'a' sets it to the end.
        :type only_write_locally: bool
        :param only_write_locally: if true, don't upload this file to Clarity.
        :type name: str
        :param name: The name that will be used if you are creating a new file.

        :rtype: File
        """
        f = self.file
        if name is not None:
            f.name = name

        f.only_write_locally = only_write_locally
        f.mode = mode

        if "w" in mode:
            f.truncate()
        elif "r" in mode:
            f.writeable = False
        elif "a" in mode:
            f.seek_to_end()

        return f

    @property
    def container(self):
        """
        From "location.container". For XML value "location.value", use Python property ``.location_value``.

        :type: Container
        """
        return self.lims.containers.from_link_node(self.xml_find("./location/container"))

    @property
    def reagent_label_names(self):
        # type: () -> list[str]
        """:type: list[str]"""
        return [l.name for l in self.reagent_labels]

    @property
    def reagent_label_name(self):
        # type: () -> str
        """:type: str"""
        label_names = self.reagent_label_names
        num_labels = len(label_names)

        if num_labels > 1:
            raise Exception("Artifact has multiple reagent labels.")

        if num_labels == 0:
            return None

        return label_names[0]

    @reagent_label_name.setter
    def reagent_label_name(self, reagent_label_name):
        # type: (str) -> None
        """
        :type reagent_label_name: str
        """
        reagent_label = self.make_subelement_with_parents("./reagent-label")
        reagent_label.set("name", reagent_label_name)

    def _get_attach_to_key(self):
        return self.type, ""
