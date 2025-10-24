import java.time.LocalDateTime;

public class User {

    private long id;
    private String name;
    private String email;
    private String passwordHash;
    private LocalDateTime createdAt;

    // A constructor for creating new users to be saved in the database.
    public User(String name, String email, String passwordHash) {
        this.name = name; // Full name of user
        this.email = email; //
        this.passwordHash = passwordHash;
    }

    // A full constructor for retrieving data from the DB
    public User(long id, String name, String email, String passwordHash, LocalDateTime createdAt) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.passwordHash = passwordHash;
        this.createdAt = createdAt;
    }

    // Getters and Setters
    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}