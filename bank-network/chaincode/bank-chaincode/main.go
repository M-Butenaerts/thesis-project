package main

import (
    "encoding/json"
    "fmt"
    "strconv"

    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
    contractapi.Contract
}

type Account struct {
    ID     string `json:"ID"`
    Balance int    `json:"balance"`
}

func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
    return nil
}

func (s *SmartContract) CreateAccount(ctx contractapi.TransactionContextInterface, ID string) error {
    exists, err := s.AccountExists(ctx, ID)
    if err != nil {
        return err
    }
    if exists {
        return fmt.Errorf("account %s already exists", ID)
    }

    acc := Account{ID: ID, Balance: 0}
    accBytes, _ := json.Marshal(acc)
    return ctx.GetStub().PutState(ID, accBytes)
}

func (s *SmartContract) GetAccount(ctx contractapi.TransactionContextInterface, ID string) (*Account, error) {
    accBytes, err := ctx.GetStub().GetState(ID)
    if err != nil {
        return nil, err
    }
    if accBytes == nil {
        return nil, fmt.Errorf("account %s does not exist", ID)
    }

    var acc Account
    _ = json.Unmarshal(accBytes, &acc)
    return &acc, nil
}

func (s *SmartContract) Transfer(ctx contractapi.TransactionContextInterface, fromID string, toID string, amountStr string) error {
    amount, err := strconv.Atoi(amountStr)
    if err != nil {
        return fmt.Errorf("invalid amount: %v", err)
    }

    fromAcc, err := s.GetAccount(ctx, fromID)
    if err != nil {
        return err
    }

    toAcc, err := s.GetAccount(ctx, toID)
    if err != nil {
        return err
    }

    // if fromAcc.Balance < amount {
    //     return fmt.Errorf("insufficient funds in account %s", fromID)
    // }

    fromAcc.Balance -= amount
    toAcc.Balance += amount

    fromBytes, _ := json.Marshal(fromAcc)
    toBytes, _ := json.Marshal(toAcc)

    if err := ctx.GetStub().PutState(fromID, fromBytes); err != nil {
        return err
    }
    return ctx.GetStub().PutState(toID, toBytes)
}
func (s *SmartContract) Deposit(ctx contractapi.TransactionContextInterface, ID string, amountStr string) error {
    amount, err := strconv.Atoi(amountStr)
    if err != nil {
        return fmt.Errorf("invalid amount: %v", err)
    }

    acc, err := s.GetAccount(ctx, ID)
    if err != nil {
        return err
    }
    
    acc.Balance += amount
    accBytes, _ := json.Marshal(acc)

    return ctx.GetStub().PutState(ID, accBytes)
}

func (s *SmartContract) withdrawal(ctx contractapi.TransactionContextInterface, ID string, amountStr string) error {
    amount, err := strconv.Atoi(amountStr)
    if err != nil {
        return fmt.Errorf("invalid amount: %v", err)
    }

    acc, err := s.GetAccount(ctx, ID)
    if err != nil {
        return err
    }
    
    acc.Balance -= amount
    accBytes, _ := json.Marshal(acc)

    return ctx.GetStub().PutState(ID, accBytes)
}

// Delete an account
func (s *SmartContract) DeleteAccount(ctx contractapi.TransactionContextInterface, ID string) error {
    exists, err := s.AccountExists(ctx, ID)
    if err != nil {
        return err
    }
    if !exists {
        return fmt.Errorf("account %s does not exist", ID)
    }
    return ctx.GetStub().DelState(ID)
}

// Check if account exists
func (s *SmartContract) AccountExists(ctx contractapi.TransactionContextInterface, ID string) (bool, error) {
    accBytes, err := ctx.GetStub().GetState(ID)
    if err != nil {
        return false, err
    }
    return accBytes != nil, nil
}

// List all accounts
func (s *SmartContract) GetAllAccounts(ctx contractapi.TransactionContextInterface) ([]*Account, error) {
    resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
    if err != nil {
        return nil, err
    }
    defer resultsIterator.Close()

    var accounts []*Account
    for resultsIterator.HasNext() {
        queryResponse, err := resultsIterator.Next()
        if err != nil {
            return nil, err
        }

        var acc Account
        _ = json.Unmarshal(queryResponse.Value, &acc)
        accounts = append(accounts, &acc)
    }

    return accounts, nil
}

func main() {
    chaincode, err := contractapi.NewChaincode(new(SmartContract))
    if err != nil {
        panic("Error creating chaincode: " + err.Error())
    }

    if err := chaincode.Start(); err != nil {
        panic("Error starting chaincode: " + err.Error())
    }
}