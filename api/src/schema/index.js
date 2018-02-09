import resolvers from './resolvers'
import { makeExecutableSchema } from 'graphql-tools'

const Schema = i18n => {
  const typeDefs = `
    scalar ForwardSortationArea

    input Filter {
      field: Field!
      gt: String
      lt: String
      eq: String
    }

    type Wall {
      label: String
      structureTypeEnglish: String
      structureTypeFrench: String
      componentTypeSizeEnglish: String
      componentTypeSizeFrench: String
      nominalRsi: Float
      nominalR: Float
      effectiveRsi: Float
      effectiveR: Float
      areaMetres: Float
      areaFeet: Float
      perimeter: Float
      height: Float
    }

    type Door {
      typeEnglish: String
      typeFrench: String
      rsi: Float
      rValue: Float
      uFactor: Float
      uFactorImperial: Float
      areaMetres: Float
      areaFeet: Float
    }

    type Window {
      label: String
      rsi: Float
      rvalue: Float
      glazingTypesEnglish: String
      glazingTypesFrench: String
      coatingsTintsEnglish: String
      coatingsTintsFrench: String
      fillTypeEnglish: String
      fillTypeFrench: String
      spacerTypeEnglish: String
      spacerTypeFrench: String
      typeEnglish: String
      typeFrench: String
      frameMaterialEnglish: String
      frameMaterialFrench: String
      areaMetres: Float
      areaFeet: Float
      width: Float
      height: Float
    }

    type Ceiling {
      label: String
      typeEnglish: String
      typeFrench: String
      nominalRsi: Float
      nominalR: Float
      effectiveRsi: Float
      effectiveR: Float
      areaMetres: Float
      areaFeet: Float
      lengthMetres: Float
      lengthFeet: Float
    }

    # ${i18n.t`This is a description of evaluations`}
    type Evaluation {
      evaluationType: String
      entryDate: String
      creationDate: String
      modificationDate: String
      ceilings: [Ceiling]
      walls: [Wall]
      doors: [Door]
      windows: [Window]
    }


    # ${i18n.t`A residential building evaluted under the Energuide program`}
    type Dwelling {
      houseId: Int
      # ${i18n.t`Year of construction`}
      yearBuilt: Int
      city: String
      region: String
      forwardSortationArea: String
      evaluations: [Evaluation]
    }

    # ${i18n.t`The root query type`}
    type Query {
      # ${i18n.t`Details for a specific dwelling`}
      evaluationsFor(account: Int!): Dwelling
      dwellingsInFSA(filter: Filter forwardSortationArea: ForwardSortationArea!): [Dwelling]
    }

    enum Field {
      houseId
      yearBuilt
      city
      region
      forwardSortationArea
    }
  `

  return makeExecutableSchema({ typeDefs, resolvers })
}

export default Schema