# -*- coding: utf-8 -*-

from obspy.core.event import ResourceIdentifier, WaveformStreamID, \
    readEvents, Event
from obspy.core.quakeml import readQuakeML, Pickler, writeQuakeML
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.util.base import NamedTemporaryFile
from xml.etree.ElementTree import tostring, fromstring
import os
import unittest
import warnings


class QuakeMLTestCase(unittest.TestCase):
    """
    Test suite for obspy.core.quakeml
    """
    def setUp(self):
        # directory where the test files are located
        self.path = os.path.join(os.path.dirname(__file__), 'data')

    def _compareStrings(self, doc1, doc2):
        """
        Simple helper function to compare two XML strings.
        """
        obj1 = fromstring(doc1)
        str1 = ''.join([s.strip() for s in tostring(obj1).splitlines()])
        obj2 = fromstring(doc2)
        str2 = ''.join([s.strip() for s in tostring(obj2).splitlines()])
        if str1 != str2:
            print
            print str1
            print str2
        self.assertEqual(str1, str2)

    def test_readQuakeML(self):
        """
        """
        # IRIS
        filename = os.path.join(self.path, 'iris_events.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 2)
        self.assertEqual(catalog[0].resource_id,
            ResourceIdentifier(
                'smi:www.iris.edu/ws/event/query?eventId=3279407'))
        self.assertEqual(catalog[1].resource_id,
            ResourceIdentifier(
                'smi:www.iris.edu/ws/event/query?eventId=2318174'))
        # NERIES
        filename = os.path.join(self.path, 'neries_events.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 3)
        self.assertEqual(catalog[0].resource_id,
            ResourceIdentifier('quakeml:eu.emsc/event/20120404_0000041'))
        self.assertEqual(catalog[1].resource_id,
            ResourceIdentifier('quakeml:eu.emsc/event/20120404_0000038'))
        self.assertEqual(catalog[2].resource_id,
            ResourceIdentifier('quakeml:eu.emsc/event/20120404_0000039'))

    def test_event(self):
        """
        Tests Event object.
        """
        filename = os.path.join(self.path, 'quakeml_1.2_event.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        event = catalog[0]
        self.assertEqual(event.resource_id,
            ResourceIdentifier('smi:ch.ethz.sed/event/historical/1165'))
        # enums
        self.assertEqual(event.event_type, 'earthquake')
        self.assertEqual(event.event_type_certainty, 'suspected')
        # comments
        self.assertEqual(len(event.comments), 2)
        c = event.comments
        self.assertEqual(c[0].text, 'Relocated after re-evaluation')
        self.assertEqual(c[0].resource_id, None)
        self.assertEqual(c[0].creation_info.agency_id, 'EMSC')
        self.assertEqual(c[1].text, 'Another comment')
        self.assertEqual(c[1].resource_id,
            ResourceIdentifier(resource_id="smi:some/comment/id/number_3"))
        self.assertEqual(c[1].creation_info, None)
        # event descriptions
        self.assertEqual(len(event.event_descriptions), 3)
        d = event.event_descriptions
        self.assertEqual(d[0].text, '1906 San Francisco Earthquake')
        self.assertEqual(d[0].type, 'earthquake name')
        self.assertEqual(d[1].text, 'NEAR EAST COAST OF HONSHU, JAPAN')
        self.assertEqual(d[1].type, 'Flinn-Engdahl region')
        self.assertEqual(d[2].text, 'free-form string')
        self.assertEqual(d[2].type, None)
        # creation info
        self.assertEqual(event.creation_info.author, "Erika Mustermann")
        self.assertEqual(event.creation_info.agency_id, "EMSC")
        self.assertEqual(event.creation_info.author_uri,
            ResourceIdentifier("smi:smi-registry/organization/EMSC"))
        self.assertEqual(event.creation_info.agency_uri,
            ResourceIdentifier("smi:smi-registry/organization/EMSC"))
        self.assertEqual(event.creation_info.creation_time,
            UTCDateTime("2012-04-04T16:40:50+00:00"))
        self.assertEqual(event.creation_info.version, "1.0.1")
        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_origin(self):
        """
        Tests Origin object.
        """
        filename = os.path.join(self.path, 'quakeml_1.2_origin.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(len(catalog[0].origins), 1)
        origin = catalog[0].origins[0]
        self.assertEqual(origin.resource_id,
            ResourceIdentifier(
            'smi:www.iris.edu/ws/event/query?originId=7680412'))
        self.assertEqual(origin.time, UTCDateTime("2011-03-11T05:46:24.1200"))
        self.assertEqual(origin.latitude, 38.297)
        self.assertEqual(origin.latitude_errors.lower_uncertainty, None)
        self.assertEqual(origin.longitude, 142.373)
        self.assertEqual(origin.longitude_errors.uncertainty, None)
        self.assertEqual(origin.depth, 29.0)
        self.assertEqual(origin.depth_errors.confidence_level, 50.0)
        self.assertEqual(origin.depth_type, "from location")
        self.assertEqual(origin.method_id,
            ResourceIdentifier(resource_id="smi:some/method/NA"))
        self.assertEqual(origin.time_fixed, None)
        self.assertEqual(origin.epicenter_fixed, False)
        self.assertEqual(origin.reference_system_id,
            ResourceIdentifier(resource_id="smi:some/reference/muh"))
        self.assertEqual(origin.earth_model_id,
            ResourceIdentifier(resource_id="smi:same/model/maeh"))
        self.assertEqual(origin.evaluation_mode, "manual")
        self.assertEqual(origin.evaluation_status, "preliminary")
        self.assertEqual(origin.origin_type, "hypocenter")
        # composite times
        self.assertEqual(len(origin.composite_times), 2)
        c = origin.composite_times
        self.assertEqual(c[0].year, 2029)
        self.assertEqual(c[0].month, None)
        self.assertEqual(c[0].day, None)
        self.assertEqual(c[0].hour, 12)
        self.assertEqual(c[0].minute, None)
        self.assertEqual(c[0].second, None)
        self.assertEqual(c[1].year, None)
        self.assertEqual(c[1].month, None)
        self.assertEqual(c[1].day, None)
        self.assertEqual(c[1].hour, 1)
        self.assertEqual(c[1].minute, None)
        self.assertEqual(c[1].second, 29.124234)
        # quality
        self.assertEqual(origin.quality.used_station_count, 16)
        self.assertEqual(origin.quality.standard_error, 0)
        self.assertEqual(origin.quality.azimuthal_gap, 231)
        self.assertEqual(origin.quality.maximum_distance, 53.03)
        self.assertEqual(origin.quality.minimum_distance, 2.45)
        self.assertEqual(origin.quality.associated_phase_count, None)
        self.assertEqual(origin.quality.associated_station_count, None)
        self.assertEqual(origin.quality.depth_phase_count, None)
        self.assertEqual(origin.quality.secondary_azimuthal_gap, None)
        self.assertEqual(origin.quality.ground_truth_level, None)
        self.assertEqual(origin.quality.median_distance, None)
        # comments
        self.assertEqual(len(origin.comments), 2)
        c = origin.comments
        self.assertEqual(c[0].text, 'Some comment')
        self.assertEqual(c[0].resource_id,
            ResourceIdentifier(resource_id="smi:some/comment/reference"))
        self.assertEqual(c[0].creation_info.author, 'EMSC')
        self.assertEqual(c[1].resource_id, None)
        self.assertEqual(c[1].creation_info, None)
        self.assertEqual(c[1].text, 'Another comment')
        # creation info
        self.assertEqual(origin.creation_info.author, "NEIC")
        self.assertEqual(origin.creation_info.agency_id, None)
        self.assertEqual(origin.creation_info.author_uri, None)
        self.assertEqual(origin.creation_info.agency_uri, None)
        self.assertEqual(origin.creation_info.creation_time, None)
        self.assertEqual(origin.creation_info.version, None)
        # origin uncertainty
        u = origin.origin_uncertainty
        self.assertEqual(u.preferred_description, "uncertainty ellipse")
        self.assertEqual(u.horizontal_uncertainty, 9000)
        self.assertEqual(u.min_horizontal_uncertainty, 6000)
        self.assertEqual(u.max_horizontal_uncertainty, 10000)
        self.assertEqual(u.azimuth_max_horizontal_uncertainty, 80.0)
        # confidence ellipsoid
        c = u.confidence_ellipsoid
        self.assertEqual(c.semi_intermediate_axis_length, 2.123)
        self.assertEqual(c.major_axis_rotation, 5.123)
        self.assertEqual(c.major_axis_plunge, 3.123)
        self.assertEqual(c.semi_minor_axis_length, 1.123)
        self.assertEqual(c.semi_major_axis_length, 0.123)
        self.assertEqual(c.major_axis_azimuth, 4.123)
        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_magnitude(self):
        """
        Tests Magnitude object.
        """
        filename = os.path.join(self.path, 'quakeml_1.2_magnitude.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(len(catalog[0].magnitudes), 1)
        mag = catalog[0].magnitudes[0]
        self.assertEqual(mag.resource_id,
            ResourceIdentifier('smi:ch.ethz.sed/magnitude/37465'))
        self.assertEqual(mag.mag, 5.5)
        self.assertEqual(mag.mag_errors.uncertainty, 0.1)
        self.assertEqual(mag.magnitude_type, 'MS')
        self.assertEqual(mag.method_id,
            ResourceIdentifier(
            'smi:ch.ethz.sed/magnitude/generic/surface_wave_magnitude'))
        self.assertEqual(mag.station_count, 8)
        self.assertEqual(mag.evaluation_status, 'preliminary')
        # comments
        self.assertEqual(len(mag.comments), 2)
        c = mag.comments
        self.assertEqual(c[0].text, 'Some comment')
        self.assertEqual(c[0].resource_id,
            ResourceIdentifier(resource_id="smi:some/comment/id/muh"))
        self.assertEqual(c[0].creation_info.author, 'EMSC')
        self.assertEqual(c[1].creation_info, None)
        self.assertEqual(c[1].text, 'Another comment')
        self.assertEqual(c[1].resource_id, None)
        # creation info
        self.assertEqual(mag.creation_info.author, "NEIC")
        self.assertEqual(mag.creation_info.agency_id, None)
        self.assertEqual(mag.creation_info.author_uri, None)
        self.assertEqual(mag.creation_info.agency_uri, None)
        self.assertEqual(mag.creation_info.creation_time, None)
        self.assertEqual(mag.creation_info.version, None)
        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_stationmagnitudecontribution(self):
        """
        Tests the station magnitude contribution object.
        """
        filename = os.path.join(self.path,
            'quakeml_1.2_stationmagnitudecontributions.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(len(catalog[0].magnitudes), 1)
        self.assertEqual(
            len(catalog[0].magnitudes[0].station_magnitude_contributions), 2)
        # Check the first stationMagnitudeContribution object.
        stat_contrib = \
            catalog[0].magnitudes[0].station_magnitude_contributions[0]
        self.assertEqual(stat_contrib.station_magnitude_id.resource_id,
            "smi:ch.ethz.sed/magnitude/station/881342")
        self.assertEqual(stat_contrib.weight, 0.77)
        self.assertEqual(stat_contrib.residual, 0.02)
        # Check the second stationMagnitudeContribution object.
        stat_contrib = \
            catalog[0].magnitudes[0].station_magnitude_contributions[1]
        self.assertEqual(stat_contrib.station_magnitude_id.resource_id,
            "smi:ch.ethz.sed/magnitude/station/881334")
        self.assertEqual(stat_contrib.weight, 0.55)
        self.assertEqual(stat_contrib.residual, 0.11)

        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_stationmagnitude(self):
        """
        Tests StationMagnitude object.
        """
        filename = os.path.join(self.path, 'quakeml_1.2_stationmagnitude.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(len(catalog[0].station_magnitudes), 1)
        mag = catalog[0].station_magnitudes[0]
        # Assert the actual StationMagnitude object. Everything that is not set
        # in the QuakeML file should be set to None.
        self.assertEqual(mag.resource_id,
            ResourceIdentifier("smi:ch.ethz.sed/magnitude/station/881342"))
        self.assertEqual(mag.origin_id,
            ResourceIdentifier('smi:some/example/id'))
        self.assertEqual(mag.mag, 6.5)
        self.assertEqual(mag.mag_errors.uncertainty, 0.2)
        self.assertEqual(mag.station_magnitude_type, 'MS')
        self.assertEqual(mag.amplitude_id,
            ResourceIdentifier("smi:ch.ethz.sed/amplitude/824315"))
        self.assertEqual(mag.method_id,
            ResourceIdentifier(
                "smi:ch.ethz.sed/magnitude/generic/surface_wave_magnitude"))
        self.assertEqual(mag.waveform_id,
            WaveformStreamID(network_code='BW', station_code='FUR',
                             resource_uri="smi:ch.ethz.sed/waveform/201754"))
        self.assertEqual(mag.creation_info, None)
        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_arrival(self):
        """
        Tests Arrival object.
        """
        filename = os.path.join(self.path, 'quakeml_1.2_arrival.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(len(catalog[0].origins[0].arrivals), 2)
        ar = catalog[0].origins[0].arrivals[0]
        # Test the actual Arrival object. Everything not set in the QuakeML
        # file should be None.
        self.assertEqual(ar.pick_id,
            ResourceIdentifier('smi:ch.ethz.sed/pick/117634'))
        self.assertEqual(ar.phase, 'Pn')
        self.assertEqual(ar.azimuth, 12.0)
        self.assertEqual(ar.distance, 0.5)
        self.assertEqual(ar.takeoff_angle, 11.0)
        self.assertEqual(ar.takeoff_angle_errors.uncertainty, 0.2)
        self.assertEqual(ar.time_residual, 1.6)
        self.assertEqual(ar.horizontal_slowness_residual, 1.7)
        self.assertEqual(ar.backazimuth_residual, 1.8)
        self.assertEqual(ar.time_weight, 0.48)
        self.assertEqual(ar.horizontal_slowness_weight, 0.49)
        self.assertEqual(ar.backazimuth_weight, 0.5)
        self.assertEqual(ar.earth_model_id,
            ResourceIdentifier('smi:ch.ethz.sed/earthmodel/U21'))
        self.assertEqual(len(ar.comments), 1)
        self.assertEqual(ar.creation_info.author, "Erika Mustermann")
        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_pick(self):
        """
        Tests Pick object.
        """
        filename = os.path.join(self.path, 'quakeml_1.2_pick.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(len(catalog[0].picks), 2)
        pick = catalog[0].picks[0]
        self.assertEqual(pick.resource_id,
            ResourceIdentifier('smi:ch.ethz.sed/pick/117634'))
        self.assertEqual(pick.time, UTCDateTime('2005-09-18T22:04:35Z'))
        self.assertEqual(pick.time_errors.uncertainty, 0.012)
        self.assertEqual(pick.waveform_id,
            WaveformStreamID(network_code='BW', station_code='FUR',
                             resource_uri='smi:ch.ethz.sed/waveform/201754'))
        self.assertEqual(pick.filter_id,
            ResourceIdentifier('smi:ch.ethz.sed/filter/lowpass/standard'))
        self.assertEqual(pick.method_id,
            ResourceIdentifier('smi:ch.ethz.sed/picker/autopicker/6.0.2'))
        self.assertEqual(pick.backazimuth, 44.0)
        self.assertEqual(pick.onset, 'impulsive')
        self.assertEqual(pick.phase_hint, 'Pn')
        self.assertEqual(pick.polarity, 'positive')
        self.assertEqual(pick.evaluation_mode, "manual")
        self.assertEqual(pick.evaluation_status, "confirmed")
        self.assertEqual(len(pick.comments), 2)
        self.assertEqual(pick.creation_info.author, "Erika Mustermann")
        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_focalmechanism(self):
        """
        Tests FocalMechanism object.
        """
        filename = os.path.join(self.path, 'quakeml_1.2_focalmechanism.xml')
        catalog = readQuakeML(filename)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(len(catalog[0].focal_mechanisms), 2)
        fm = catalog[0].focal_mechanisms[0]
        # general
        self.assertEqual(fm.resource_id,
            ResourceIdentifier('smi:ISC/fmid=292309'))
        self.assertEqual(fm.waveform_id.network_code, 'BW')
        self.assertEqual(fm.waveform_id.station_code, 'FUR')
        self.assertEqual(fm.waveform_id.resource_uri,
            ResourceIdentifier(resource_id="smi:ch.ethz.sed/waveform/201754"))
        self.assertTrue(isinstance(fm.waveform_id, WaveformStreamID))
        self.assertEqual(fm.triggering_origin_id,
            ResourceIdentifier('smi:originId=7680412'))
        self.assertAlmostEqual(fm.azimuthal_gap, 0.123)
        self.assertEqual(fm.station_polarity_count, 987)
        self.assertAlmostEqual(fm.misfit, 1.234)
        self.assertAlmostEqual(fm.station_distribution_ratio, 2.345)
        self.assertEqual(fm.method_id,
            ResourceIdentifier('smi:ISC/methodID=Best_double_couple'))
        # comments
        self.assertEqual(len(fm.comments), 2)
        c = fm.comments
        self.assertEqual(c[0].text, 'Relocated after re-evaluation')
        self.assertEqual(c[0].resource_id, None)
        self.assertEqual(c[0].creation_info.agency_id, 'MUH')
        self.assertEqual(c[1].text, 'Another MUH')
        self.assertEqual(c[1].resource_id,
            ResourceIdentifier(resource_id="smi:some/comment/id/number_3"))
        self.assertEqual(c[1].creation_info, None)
        # creation info
        self.assertEqual(fm.creation_info.author, "Erika Mustermann")
        self.assertEqual(fm.creation_info.agency_id, "MUH")
        self.assertEqual(fm.creation_info.author_uri,
            ResourceIdentifier("smi:smi-registry/organization/MUH"))
        self.assertEqual(fm.creation_info.agency_uri,
            ResourceIdentifier("smi:smi-registry/organization/MUH"))
        self.assertEqual(fm.creation_info.creation_time,
            UTCDateTime("2012-04-04T16:40:50+00:00"))
        self.assertEqual(fm.creation_info.version, "1.0.1")
        # nodalPlanes
        self.assertAlmostEqual(fm.nodal_planes.nodal_plane_1.strike, 346.0)
        self.assertAlmostEqual(fm.nodal_planes.nodal_plane_1.dip, 57.0)
        self.assertAlmostEqual(fm.nodal_planes.nodal_plane_1.rake, 75.0)
        self.assertAlmostEqual(fm.nodal_planes.nodal_plane_2.strike, 193.0)
        self.assertAlmostEqual(fm.nodal_planes.nodal_plane_2.dip, 36.0)
        self.assertAlmostEqual(fm.nodal_planes.nodal_plane_2.rake, 112.0)
        self.assertEqual(fm.nodal_planes.preferred_plane, 2)
        # principalAxes
        self.assertAlmostEqual(fm.principal_axes.t_axis.azimuth, 216.0)
        self.assertAlmostEqual(fm.principal_axes.t_axis.plunge, 73.0)
        self.assertAlmostEqual(fm.principal_axes.t_axis.length, 1.050e+18)
        self.assertAlmostEqual(fm.principal_axes.p_axis.azimuth, 86.0)
        self.assertAlmostEqual(fm.principal_axes.p_axis.plunge, 10.0)
        self.assertAlmostEqual(fm.principal_axes.p_axis.length, -1.180e+18)
        self.assertEqual(fm.principal_axes.n_axis.azimuth, None)
        self.assertEqual(fm.principal_axes.n_axis.plunge, None)
        self.assertEqual(fm.principal_axes.n_axis.length, None)
        # momentTensor
        mt = fm.moment_tensor
        self.assertEqual(mt.derived_origin_id,
            ResourceIdentifier('smi:ISC/origid=13145006'))
        self.assertAlmostEqual(mt.scalar_moment, 1.100e+18)
        self.assertAlmostEqual(mt.tensor.m_rr, 9.300e+17)
        self.assertAlmostEqual(mt.tensor.m_tt, 1.700e+17)
        self.assertAlmostEqual(mt.tensor.m_pp, -1.100e+18)
        self.assertAlmostEqual(mt.tensor.m_rt, -2.200e+17)
        self.assertAlmostEqual(mt.tensor.m_rp, 4.000e+17)
        self.assertAlmostEqual(mt.tensor.m_tp, 3.000e+16)
        self.assertAlmostEqual(mt.clvd, 0.22)
        # exporting back to XML should result in the same document
        original = open(filename, "rt").read()
        processed = Pickler().dumps(catalog)
        self._compareStrings(original, processed)

    def test_writeQuakeML(self):
        """
        Tests writing a QuakeML document.
        """
        filename = os.path.join(self.path, 'qml-example-1.2-RC3.xml')
        with NamedTemporaryFile() as tf:
            tmpfile = tf.name
            catalog = readQuakeML(filename)
            self.assertTrue(len(catalog), 1)
            writeQuakeML(catalog, tmpfile)
            # Read file again. Avoid the (legit) warning about the already used
            # resource identifiers.
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("ignore")
                catalog2 = readQuakeML(tmpfile)
        self.assertTrue(len(catalog2), 1)

    def test_readEvents(self):
        """
        Tests reading a QuakeML document via readEvents.
        """
        filename = os.path.join(self.path, 'neries_events.xml')
        with NamedTemporaryFile() as tf:
            tmpfile = tf.name
            catalog = readEvents(filename)
            self.assertTrue(len(catalog), 3)
            catalog.write(tmpfile, format='QUAKEML')
            # Read file again. Avoid the (legit) warning about the already used
            # resource identifiers.
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("ignore")
                catalog2 = readEvents(tmpfile)
        self.assertTrue(len(catalog2), 3)

    def test_enums(self):
        """
        Parses the QuakeML xsd scheme definition and checks if all enums are
        correctly defined.

        This is a very strict test against the xsd scheme file of QuakeML 1.2.
        If obspy.core.event will ever be more loosely coupled to QuakeML this
        test WILL HAVE to be changed.
        """
        # Currently only works with lxml.
        try:
            from lxml.etree import parse
        except:
            return
        xsd_enum_definitions = {}
        xsd_file = os.path.join(self.path, "..", "..", "docs",
            "QuakeML-BED-1.2.xsd")
        root = parse(xsd_file).getroot()

        # Get all enums from the xsd file.
        for stype in root.findall("xs:simpleType", namespaces=root.nsmap):
            type_name = stype.get("name")
            restriction = stype.find("xs:restriction", namespaces=root.nsmap)
            if restriction is None:
                continue
            if restriction.get("base") != "xs:string":
                continue
            enums = restriction.findall("xs:enumeration",
                namespaces=root.nsmap)
            if not enums:
                continue
            enums = [_i.get("value") for _i in enums]
            xsd_enum_definitions[type_name] = enums

        # Now import all enums and check if they are correct.
        from obspy.core import event_header
        from obspy.core.util.types import Enum
        available_enums = {}
        for module_item_name in dir(event_header):
            module_item = getattr(event_header, module_item_name)
            if type(module_item) != Enum:
                continue
            # Assign clearer names.
            enum_name = module_item_name
            enum_values = [_i.lower() for _i in module_item.keys()]
            available_enums[enum_name] = enum_values
        # Now loop over all enums defined in the xsd file and check them.
        for enum_name, enum_items in xsd_enum_definitions.iteritems():
            self.assertTrue(enum_name in available_enums.keys())
            # Check that also all enum items are available.
            available_items = available_enums[enum_name]
            available_items = [_i.lower() for _i in available_items]
            for enum_item in enum_items:
                if enum_item.lower() not in available_items:
                    msg = "Value '%s' not in Enum '%s'" % (enum_item,
                        enum_name)
                    raise Exception(msg)
            # Check if there are too many items.
            if len(available_items) != len(enum_items):
                additional_items = [_i for _i in available_items
                    if _i.lower() not in enum_items]
                msg = "Enum {enum_name} has the following additional items" + \
                    " not defined in the xsd style sheet:\n\t{enumerations}"
                msg = msg.format(enum_name=enum_name,
                    enumerations=", ".join(additional_items))
                raise Exception(msg)

    def test_read_string(self):
        """
        Test reading a QuakeML string/unicode object via readEvents.
        """
        filename = os.path.join(self.path, 'neries_events.xml')
        data = open(filename, 'rt').read()
        catalog = readEvents(data)
        self.assertEqual(len(catalog), 3)

    def test_preferred_tags(self):
        """
        Testing preferred magnitude, origin and focal mechanism tags
        """
        # testing empty event
        ev = Event()
        self.assertEqual(ev.preferred_origin(), None)
        self.assertEqual(ev.preferred_magnitude(), None)
        self.assertEqual(ev.preferred_focal_mechanism(), None)
        # testing existing event
        filename = os.path.join(self.path, 'preferred.xml')
        catalog = readEvents(filename)
        self.assertEqual(len(catalog), 1)
        ev_str = "Event:\t2012-12-12T05:46:24.120000Z | +38.297, +142.373 " + \
                 "| 2.0 MW"
        self.assertTrue(ev_str in str(catalog.events[0]))
        # testing ids
        ev = catalog.events[0]
        self.assertEqual('smi:orig2', ev.preferred_origin_id)
        self.assertEqual('smi:mag2', ev.preferred_magnitude_id)
        self.assertEqual('smi:fm2', ev.preferred_focal_mechanism_id)
        # testing objects
        self.assertEqual(ev.preferred_origin(), ev.origins[1])
        self.assertEqual(ev.preferred_magnitude(), ev.magnitudes[1])
        self.assertEqual(ev.preferred_focal_mechanism(),
            ev.focal_mechanisms[1])


def suite():
    return unittest.makeSuite(QuakeMLTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
