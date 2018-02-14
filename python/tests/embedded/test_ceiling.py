import pytest
from energuide import bilingual
from energuide import element
from energuide.embedded import area
from energuide.embedded import ceiling
from energuide.embedded import distance
from energuide.embedded import insulation


@pytest.fixture
def sample_raw() -> element.Element:
    data = """
<Ceiling>
    <Label>Main attic</Label>
    <Construction>
        <Type>
            <English>Attic/gable</English>
            <French>Combles/pignon</French>
        </Type>
        <CeilingType nominalInsulation='2.864' rValue='2.9463' />
    </Construction>
    <Measurements area='46.4515' length='23.875' />
</Ceiling>
    """
    return element.Element.from_string(data)


@pytest.fixture
def sample() -> ceiling.Ceiling:
    return ceiling.Ceiling(
        label='Main attic',
        ceiling_type=bilingual.Bilingual(english='Attic/gable', french='Combles/pignon'),
        nominal_insulation=insulation.Insulation(2.864),
        effective_insulation=insulation.Insulation(2.9463),
        ceiling_area=area.Area(46.4515),
        ceiling_length=distance.Distance(23.875),
    )


def test_from_data(sample_raw: element.Element, sample: ceiling.Ceiling) -> None:
    output = ceiling.Ceiling.from_data(sample_raw)
    assert output == sample


def test_to_dict(sample: ceiling.Ceiling) -> None:
    output = sample.to_dict()
    assert output == {
        'label': 'Main attic',
        'typeEnglish': 'Attic/gable',
        'typeFrench': 'Combles/pignon',
        'insulationNominalRsi': 2.864,
        'insulationNominalR': 16.262546197168,
        'insulationEffectiveRsi': 2.9463,
        'insulationEffectiveR': 16.729867269803098,
        'areaMetres': 46.4515,
        'areaFeet': 499.9998167217784,
        'lengthMetres': 23.875,
        'lengthFeet': 78.330055,
    }